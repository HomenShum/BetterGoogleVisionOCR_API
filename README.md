# BetterGoogleVisionOCR_API

Two Python commands turn a PDF stored in Google Cloud Storage into one local JSON file containing its pages in numeric order. The first submits Google Vision document OCR; the second downloads the completed output batches, preserves blank pages, and joins them.

**Readiness:** small command-line scripts, with offline workflow tests. No web application or LLM agent is included. A real Google OCR run, cloud permissions, recognition accuracy, and deployment are not verified by the offline tests.

## Start here

- [Submit a PDF for OCR](googleVisionBatchExtract.py)
- [Export the completed pages](googleVisionPDFtextout.py)
- [Offline regression tests](tests/test_workflow.py)
- [Changes by surface](CHANGELOG/README.md)

## Install

Use Python 3.10 or later. Local verification used Python 3.11 on Windows. The workflow below is configured for Python 3.11 on Ubuntu 24.04; this is not coverage of every Python version or operating system.

~~~powershell
git clone https://github.com/HomenShum/BetterGoogleVisionOCR_API.git
cd BetterGoogleVisionOCR_API
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

On macOS/Linux, use `python3 -m venv .venv` and `source .venv/bin/activate`, then the same install command. The two direct dependencies are Google's Vision and Storage clients; no OpenAI key is needed.

Both help commands work without Google credentials and do not submit requests:

~~~text
python googleVisionBatchExtract.py --help
python googleVisionPDFtextout.py --help
~~~

## Run the two-step workflow

First set up your own Google Cloud project, billing, Vision API access, bucket permissions, and [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc). Keep credentials outside this repository. The scripts use the caller's authentication settings and do not replace `GOOGLE_APPLICATION_CREDENTIALS`.

Upload the PDF to a bucket you control, then pass **the same PDF URI to both commands**:

~~~text
python googleVisionBatchExtract.py "gs://your-bucket/reports/Research.report.pdf"
python googleVisionPDFtextout.py "gs://your-bucket/reports/Research.report.pdf"
~~~

1. BatchExtract makes a Google Vision request, writes batches of 10 pages beneath `gs://your-bucket/reports/Research.report_output/`, and waits up to 420 seconds for completion.
2. PDFtextout reads that prefix, sorts pages by Google's `context.pageNumber`, and creates `json_out/Research.report.json` relative to your current directory. It does not run OCR again.

The batch command can incur Google charges. Skip it when the completed OCR batches already exist. Rerunning it uses the same output prefix and can overwrite existing cloud batches; see [Google's PDF OCR guide](https://docs.cloud.google.com/vision/docs/pdf). Local export replaces the matching JSON file, so use separate working directories for PDFs with the same filename or simultaneous exports of the same PDF.

Example export:

~~~json
[
  {"page_number": 1, "text": "Text from the first page"},
  {"page_number": 2, "text": "No text found"}
]
~~~

Blank pages retain the existing `No text found` marker. Directory markers and non-JSON objects are skipped. Missing results, malformed JSON, storage failures, and reported page errors exit unsuccessfully before replacing an existing export. A local disk-write failure can still interrupt a write; this is a script, not a durable job service.

## Verify without cloud access

~~~text
python -m unittest discover -s tests -v
~~~

The standard-library tests run both actual scripts in isolated processes with fake Google SDKs and networking blocked. They cover explicit PDF selection, preserved authentication, fresh output folders, page ordering, Unicode and blank pages, help and invalid inputs, provider failures, six concurrent isolated exports, and ten repeated exports.

These tests prove the local command and output contract. They do not call Google, measure OCR quality, validate a user's permissions, certify large or malicious cloud payload handling, or prove a production deployment. The [offline verification workflow](.github/workflows/verify.yml) installs the dependencies, checks imports and help, and runs this suite on pull requests and main pushes without Google credentials or OCR calls. Read its result at the exact commit before claiming CI passed.

## Troubleshooting and handoff

- **`No module named 'google'`:** activate the environment and install this repository's `requirements.txt`.
- **Credentials or permission error:** follow Google's authentication guide and verify access to your input object and output prefix.
- **`No OCR pages found`:** check that the first command completed successfully and both commands used exactly the same PDF URI.
- **Timeout or OCR page error:** inspect the original Google operation/output before retrying; a failed export does not mean OCR was free or never ran.

Historical source-editing examples remain in Git history. New contributors should start with the explicit commands above and keep test fixtures separate from real documents.
