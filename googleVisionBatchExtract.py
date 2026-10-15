"""Submit one PDF from Cloud Storage to Google Vision document OCR."""
import argparse
import re


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gcs_uri", help="PDF to process, for example gs://your-bucket/report.pdf")
    args = parser.parse_args()
    match = re.fullmatch(r"gs://([^/]+)/(.+)", args.gcs_uri)
    if not match or not match.group(2).lower().endswith(".pdf"):
        parser.error("gcs_uri must be a gs://bucket/path.pdf URI")

    from google.cloud import vision

    destination_uri = args.gcs_uri[:-4] + "_output/"
    request = vision.AsyncAnnotateFileRequest(
        features=[vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)],
        input_config=vision.InputConfig(
            gcs_source=vision.GcsSource(uri=args.gcs_uri),
            mime_type="application/pdf",
        ),
        output_config=vision.OutputConfig(
            gcs_destination=vision.GcsDestination(uri=destination_uri),
            batch_size=10,
        ),
    )
    operation = vision.ImageAnnotatorClient().async_batch_annotate_files(requests=[request])
    print("Waiting for the operation to finish.")
    operation.result(timeout=420)
    print(f"OCR output: {destination_uri}")


if __name__ == "__main__":
    main()
