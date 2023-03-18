# OCRTools
Resolves the issue where on the stackoverflow and google vision documentation some of their OCR usage codes don't work

Original Google Vision API Documentation 
- Intended to: Display the full text from the first page of a pdf that has been stored in a google cloud storage's bucket
- Problem is there are no further documentation guidance for new developers to use this tool effectively.
BetterGoogleVisionOCR_API solves for: 
1. What if I wanted to display multiple pages of text but the original documentation don't have instruction for it ?
2. What if some pages don't have any texts -> which would result in keyError: annotation = first_page_response['fullTextAnnotation'] ?
3. What if I don't know where I should input the google cloud storage uri within the code for the original documentataion ? 

--- Solutions that I provide ---
INSTRUCTION STEPS:
1. Set up TWO .py files

2. ie. "googleVisionBatchExtract.py" - This is for grouping up the pdf pages and extracting texts into json files, then it will store the batched up json files inside the google cloud storage
2a. create a project on google cloud
2b. get google application credentials and store into your files, this/the project helps google to charge your account for your usage
2c. store pdf file that needs to be text extracted onto your google cloud storage folder (also called the bucket); for example below, I have my bucket named pdf_test_hs. This/gcs helps google to utilize their technology on your files.
2d. get the "gsutil URI"; click on the pdf file in your gcs, the hyperlink will take you to the pdf details page, within the detail table you will find the "gsutil URI"
2e. insert your gsutil URI into the gcs_list, if you replace the existing URI and only have one gsutil URI, then put gcs_list_selected = gcs_list[0]
2f. *** batch_size = 10; may run into issues if your 10 pages of text exceeds 10mb size, so decrease the size if necessary, but I don't think many pdf pages will have more than 10mb of pure texts...
RUN PYTHON FILE => GO TO STEP 3

3. create "googleVisionPDFtextout.py" - This is to move the extracted texts out of the google cloud storage; Since there can be multiple json files that contain different chunks of the pdf text stored in non-desired order, I wrote this so it can sort through MULTIPLE json files in the CORRECT INDEX ORDER and concatenate the texts to ONE big file for data manipulation later

--- Below is the original code ---
https://cloud.google.com/vision/docs/pdf
def async_detect_document(gcs_source_uri, gcs_destination_uri):
    """OCR with PDF/TIFF as source files on GCS"""
    import json
    import re
    from google.cloud import vision
    from google.cloud import storage

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = 'application/pdf'

    # How many pages should be grouped into each json output file.
    batch_size = 2

    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)

    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.
    storage_client = storage.Client()

    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(bucket_name)

    # List objects with the given prefix, filtering out folders.
    blob_list = [blob for blob in list(bucket.list_blobs(
        prefix=prefix)) if not blob.name.endswith('/')]
    print('Output files:')
    for blob in blob_list:
        print(blob.name)

    # Process the first output file from GCS.
    # Since we specified batch_size=2, the first response contains
    # the first two pages of the input file.
    output = blob_list[0]

    json_string = output.download_as_string()
    response = json.loads(json_string)

    # The actual response for the first page of the input file.
    first_page_response = response['responses'][0]
    annotation = first_page_response['fullTextAnnotation']

    # Here we print the full text from the first page.
    # The response contains more information:
    # annotation/pages/blocks/paragraphs/words/symbols
    # including confidence scores and bounding boxes
    print('Full text:\n')
    print(annotation['text'])

