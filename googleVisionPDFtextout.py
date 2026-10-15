"""Export a PDF's completed Google Vision batches as ordered page-text JSON."""
import argparse
import json
from pathlib import Path
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gcs_uri", help="Same PDF submitted to BatchExtract, for example gs://your-bucket/report.pdf")
    args = parser.parse_args()
    match = re.fullmatch(r"gs://([^/]+)/(.+)", args.gcs_uri)
    if not match or not match.group(2).lower().endswith(".pdf"):
        parser.error("gcs_uri must be a gs://bucket/path.pdf URI")
    bucket_name, object_name = match.groups()
    prefix = object_name[:-4] + "_output/"

    from google.cloud import storage

    bucket = storage.Client().get_bucket(bucket_name)
    pages = []
    for blob in bucket.list_blobs(prefix=prefix):
        if not blob.name.endswith(".json"):
            continue
        response = json.loads(blob.download_as_bytes())
        for page in response["responses"]:
            if page.get("error"):
                raise RuntimeError(f"OCR page failed: {page['error']}")
            text = page["fullTextAnnotation"]["text"] if "fullTextAnnotation" in page else "No text found"
            pages.append({"page_number": page["context"]["pageNumber"], "text": text})
    if not pages:
        raise RuntimeError(f"No OCR pages found at gs://{bucket_name}/{prefix}; run BatchExtract first")
    pages.sort(key=lambda page: page["page_number"])

    output_dir = Path("json_out")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (object_name.rsplit("/", 1)[-1][:-4] + ".json")
    output_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported {len(pages)} pages to {output_path}")


if __name__ == "__main__":
    main()
