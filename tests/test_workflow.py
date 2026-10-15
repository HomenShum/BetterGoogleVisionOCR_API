"""Run script-level workflow checks with fake SDKs and networking blocked."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(os.environ.get("OCR_TEST_REPO", Path(__file__).resolve().parents[1]))
SOURCE = "gs://offline-bucket/reports/Research.report.pdf"
PREFIX = "reports/Research.report_output/"
EXPECTED = [
    {"page_number": 1, "text": "First page: \u4e2d\u6587"},
    {"page_number": 2, "text": "No text found"},
    {"page_number": 11, "text": "Last page"},
]
BLOBS = [
    {"name": PREFIX + "output-11-to-11.json", "data": {"responses": [{"context": {"pageNumber": 11}, "fullTextAnnotation": {"text": "Last page"}}]}},
    {"name": PREFIX + "output-1-to-2.json", "data": {"responses": [{"context": {"pageNumber": 2}}, {"context": {"pageNumber": 1}, "fullTextAnnotation": {"text": "First page: \u4e2d\u6587"}}]}},
]
LAUNCH = r"""
import json, os, pathlib, runpy, socket, sys, types
state=json.loads(os.environ['OCR_OFFLINE_STATE']); calls=[]
def record(kind, **kwargs):
    calls.append({'kind':kind, **kwargs})
    pathlib.Path('calls.json').write_text(json.dumps(calls),encoding='utf-8')
def blocked(*a, **kw): raise AssertionError('Network forbidden in offline workflow')
socket.socket.connect=blocked; socket.create_connection=blocked
google=types.ModuleType('google'); cloud=types.ModuleType('google.cloud')
vision=types.ModuleType('google.cloud.vision'); storage=types.ModuleType('google.cloud.storage')
class Message:
    def __init__(self, **kwargs): self.__dict__.update(kwargs)
class Feature(Message):
    Type=types.SimpleNamespace(DOCUMENT_TEXT_DETECTION='DOCUMENT_TEXT_DETECTION')
class Operation:
    def result(self, timeout):
        record('result',timeout=timeout)
        if state.get('batch_error'): raise RuntimeError(state['batch_error'])
class VisionClient:
    def __init__(self): record('vision_client',credentials=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    def async_batch_annotate_files(self, requests):
        req=requests[0]
        record('batch',source=req.input_config.gcs_source.uri,destination=req.output_config.gcs_destination.uri,mime=req.input_config.mime_type,batch_size=req.output_config.batch_size)
        return Operation()
class Blob:
    def __init__(self, spec): self.spec=spec; self.name=spec['name']
    def download_as_bytes(self, **kwargs):
        record('download',name=self.name)
        if 'error' in self.spec: raise RuntimeError(self.spec['error'])
        return self.spec.get('raw',json.dumps(self.spec.get('data'))).encode('utf-8')
    download_as_string=download_as_bytes
class Bucket:
    def list_blobs(self, prefix):
        record('list',prefix=prefix)
        return (Blob(b) for b in state.get('blobs',[]) if b['name'].startswith(prefix))
class StorageClient:
    def __init__(self): record('storage_client',credentials=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    def get_bucket(self, name):
        record('bucket',name=name)
        if state.get('storage_error'): raise RuntimeError(state['storage_error'])
        return Bucket()
vision.Feature=Feature; vision.ImageAnnotatorClient=VisionClient
for name in ('GcsSource','InputConfig','GcsDestination','OutputConfig','AsyncAnnotateFileRequest'): setattr(vision,name,Message)
storage.Client=StorageClient; cloud.vision=vision; cloud.storage=storage; google.cloud=cloud
sys.modules.update({'google':google,'google.cloud':cloud,'google.cloud.vision':vision,'google.cloud.storage':storage})
sys.argv=sys.argv[1:]
runpy.run_path(sys.argv[0],run_name='__main__')
"""

def invoke(script, folder, args=None, state=None):
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP") if key in os.environ}
    env.update({"PYTHONDONTWRITEBYTECODE": "1", "GOOGLE_APPLICATION_CREDENTIALS": "offline-sentinel-do-not-replace", "OCR_OFFLINE_STATE": json.dumps(state or {"blobs": BLOBS})})
    result = subprocess.run([sys.executable, "-c", LAUNCH, str(REPO / script), *(args if args is not None else [SOURCE])], cwd=folder, env=env, capture_output=True, text=True, timeout=15, encoding="utf-8")
    calls = json.loads((Path(folder) / "calls.json").read_text(encoding="utf-8")) if (Path(folder) / "calls.json").exists() else []
    return result, calls

class OfflineWorkflow(unittest.TestCase):
    def test_declared_install_matches_runtime_imports(self):
        requirements = (REPO / "requirements.txt").read_text(encoding="utf-8").lower()
        self.assertIn("google-cloud-vision", requirements)
        self.assertIn("google-cloud-storage", requirements)
        for unused in ("openai", "flask", "numpy", "sqlalchemy", "gunicorn"):
            self.assertNotIn(unused, requirements)

    def test_developer_can_request_help_without_clients(self):
        for script in ("googleVisionBatchExtract.py", "googleVisionPDFtextout.py"):
            with self.subTest(script=script), tempfile.TemporaryDirectory() as folder:
                result, calls = invoke(script, folder, ["--help"])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("gs://", result.stdout)
                self.assertEqual(calls, [])

    def test_missing_or_invalid_pdf_is_rejected_before_google(self):
        for script in ("googleVisionBatchExtract.py", "googleVisionPDFtextout.py"):
            for args in ([], ["https://example.test/report.pdf"], ["gs://bucket/"], ["gs://bucket/report.txt"], ["gs://bucket.pdf/nested/report"]):
                with self.subTest(script=script, args=args), tempfile.TemporaryDirectory() as folder:
                    result, calls = invoke(script, folder, args)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertEqual(calls, [])
                    self.assertFalse((Path(folder) / "json_out").exists())

    def test_batch_uses_explicit_pdf_and_preserves_authentication(self):
        with tempfile.TemporaryDirectory() as folder:
            result, calls = invoke("googleVisionBatchExtract.py", folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(next(c for c in calls if c["kind"] == "vision_client")["credentials"], "offline-sentinel-do-not-replace")
            self.assertEqual(next(c for c in calls if c["kind"] == "batch"), {"kind": "batch", "source": SOURCE, "destination": "gs://offline-bucket/" + PREFIX, "mime": "application/pdf", "batch_size": 10})
            self.assertEqual(next(c for c in calls if c["kind"] == "result")["timeout"], 420)

    def test_fresh_export_orders_batches_preserves_unicode_and_blank_page(self):
        with tempfile.TemporaryDirectory() as folder:
            result, calls = invoke("googleVisionPDFtextout.py", folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((Path(folder) / "json_out/Research.report.json").read_text(encoding="utf-8")), EXPECTED)
            self.assertEqual(next(c for c in calls if c["kind"] == "bucket")["name"], "offline-bucket")
            self.assertEqual(next(c for c in calls if c["kind"] == "list")["prefix"], PREFIX)
            self.assertEqual(next(c for c in calls if c["kind"] == "storage_client")["credentials"], "offline-sentinel-do-not-replace")
            self.assertFalse(any(c["kind"] == "vision_client" for c in calls))

    def test_folder_and_unrelated_objects_are_not_downloaded(self):
        state = {"blobs": [*BLOBS, {"name": PREFIX}, {"name": PREFIX + "notes.txt", "raw": "not JSON"}, {"name": "unrelated/output-1-to-2.json", "raw": "not JSON"}]}
        with tempfile.TemporaryDirectory() as folder:
            result, calls = invoke("googleVisionPDFtextout.py", folder, state=state)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([c["name"] for c in calls if c["kind"] == "download"], [b["name"] for b in BLOBS])

    def test_empty_prefix_never_writes_a_successful_empty_export(self):
        with tempfile.TemporaryDirectory() as folder:
            result, _ = invoke("googleVisionPDFtextout.py", folder, state={"blobs": []})
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(folder) / "json_out/Research.report.json").exists())

    def test_google_errors_and_malformed_json_do_not_replace_existing_output(self):
        states = [
            {"storage_error": "permission denied"},
            {"blobs": [{"name": PREFIX + "output-1-to-1.json", "raw": "{"}]},
            {"blobs": [{"name": PREFIX + "output-1-to-1.json", "data": {"responses": [{"context": {"pageNumber": 1}, "error": {"code": 13, "message": "OCR failed"}}]}}]},
        ]
        for state in states:
            with self.subTest(state=state), tempfile.TemporaryDirectory() as folder:
                output = Path(folder) / "json_out/Research.report.json"
                output.parent.mkdir()
                output.write_text("existing output must survive", encoding="utf-8")
                result, _ = invoke("googleVisionPDFtextout.py", folder, state=state)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output.read_text(encoding="utf-8"), "existing output must survive")

    def test_batch_timeout_is_not_reported_as_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            result, calls = invoke("googleVisionBatchExtract.py", folder, state={"batch_error": "operation timed out"})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("operation timed out", result.stderr)
            self.assertFalse((Path(folder) / "json_out").exists())

    def test_parallel_documents_use_isolated_output_directories(self):
        with tempfile.TemporaryDirectory() as root:
            folders = [Path(root) / str(i) for i in range(6)]
            for folder in folders: folder.mkdir()
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                results = list(pool.map(lambda folder: invoke("googleVisionPDFtextout.py", folder), folders))
            for folder, (result, _) in zip(folders, results):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads((folder / "json_out/Research.report.json").read_text(encoding="utf-8")), EXPECTED)

    def test_repeated_export_does_not_accumulate_pages_or_delete_other_files(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "json_out"
            output.mkdir()
            unrelated = output / "keep.txt"
            unrelated.write_text("keep", encoding="utf-8")
            for _ in range(10):
                result, _ = invoke("googleVisionPDFtextout.py", folder)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads((output / "Research.report.json").read_text(encoding="utf-8")), EXPECTED)
                self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")
            self.assertEqual(sorted(p.name for p in output.iterdir()), ["Research.report.json", "keep.txt"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
