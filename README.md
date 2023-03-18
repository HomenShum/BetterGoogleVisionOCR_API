# OCRTools
Resolves the issue where on the stackoverflow and google vision documentation some of their OCR usage codes don't work

Original Google Vision API Documentation 
- Intended to: Display the full text from the first page of a pdf that has been stored in a google cloud storage's bucket
- Problem is there are no further documentation guidance for new developers to use this tool effectively.
BetterGoogleVisionOCR_API solves for: 
1. What if I wanted to display multiple pages' texts ?
2. What if some pages don't have a text which would show error text on code -> annotation = first_page_response['fullTextAnnotation'] ?
3. What if I don't know where I should input the google cloud storage uri ? 

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

--- googleVisionBatchExtract.py ---

### Skip if json batch folder already created in bucket

# 1 pdf page is a unit, 1000 unit free per month
# IN FUTURE: SORT THROUGH LIST OF PDF FILES IN GCS BUCKET THEN PROCESS SELECTED PDF FILES

import os  # for file handling and image processing
import re  # re for regular expression
from google.cloud import vision
from google.cloud import storage
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'credentials\ProjectName-XYZXYZ-XYZXYZXYZYXZYXZY.json'
client = vision.ImageAnnotatorClient()

batch_size = 10  # The number of pages to process per batch.
mime_type = 'application/pdf'
feature = vision.Feature(
    type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
'''
gs://pdf_test_hs/the-autobiography-of-nelson-mandela.pdf
gs://pdf_test_hs/Citation Correction.pdf
gs://pdf_test_hs/PGE_document.pdf
gs://pdf_test_hs/RENTCafe_LeaseAgreement_Executed (2).pdf
'''

# INSTRUCTION: ADD NEW PDF FILE FROM GCS TO THE gcs_list
gcs_list = [
    'gs://pdf_test_hs/the-autobiography-of-nelson-mandela.pdf', 
    'gs://pdf_test_hs/Citation Correction.pdf', 
    'gs://pdf_test_hs/PGE_document.pdf', 
    'gs://pdf_test_hs/RENTCafe_LeaseAgreement_Executed (2).pdf']

# INSTRUCTION: SELCT THE PDF FILE BY CHANGING THE INDEX OF THE gcs_list_selected
gcs_list_selected = gcs_list[3]
# keep only the name the-autobiography-of-nelson-mandela from the uri
gcs_list_selected_name = gcs_list_selected.split('/')[-1].split('.')[0]

gcs_source_uri = gcs_list_selected
gcs_source = vision.GcsSource(uri=gcs_source_uri)
input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

gcs_destination_uri = gcs_list_selected.replace('.pdf', '_output/')
gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
output_config = vision.OutputConfig(
    gcs_destination=gcs_destination, batch_size=batch_size)

async_request = vision.AsyncAnnotateFileRequest(
    features=[feature], input_config=input_config, output_config=output_config)

operation = client.async_batch_annotate_files(requests=[async_request])
print('Waiting for the operation to finish.')
operation.result(timeout=420)

--- googleVisionPDFtextout.py ---
# INSTRUCTION: 
"""
3a. make sure to change your credentials file path
3b. comment/uncomment codes for desired format output by highlighting the codes under the label such as "# # sore in csv file", then ctrl + /
3c. same as STEP 2, copy and paste the "gsutil URI" into the "gcs_list", if there is only one link after you replaced all four of my gsutil URI, then make sure gcs_list_selected = gcs_list[0]
"""
# END OF INSTRUCTION 

import os  # for file handling and image processing
import re  # re for regular expression
from google.cloud import vision
from google.cloud import storage
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'credentials\PROJECTNAME-XYZXYZ-XYZXYZXYZXYZXYZYXZ.json'
client = vision.ImageAnnotatorClient()

batch_size = 10  # The number of pages to process per batch.
mime_type = 'application/pdf'
feature = vision.Feature(
    type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
'''
gs://pdf_test_hs/the-autobiography-of-nelson-mandela.pdf
gs://pdf_test_hs/Citation Correction.pdf
gs://pdf_test_hs/PGE_document.pdf
gs://pdf_test_hs/RENTCafe_LeaseAgreement_Executed (2).pdf
'''

gcs_list = ['gs://pdf_test_hs/the-autobiography-of-nelson-mandela.pdf', 'gs://pdf_test_hs/Citation Correction.pdf', 'gs://pdf_test_hs/PGE_document.pdf', 'gs://pdf_test_hs/RENTCafe_LeaseAgreement_Executed (2).pdf']

gcs_list_selected = gcs_list[0]
#keep only the name of the pdf from the gcs_list
gcs_list_selected_name = gcs_list_selected.split('/')[-1].split('.')[0]

gcs_source_uri = gcs_list_selected
gcs_destination_uri = gcs_list_selected.replace('.pdf', '_output/')

storage_client = storage.Client()
# match the pattern of the uri
match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
bucket_name = match.group(1)
prefix = match.group(2)
# used for listing the files in the bucket
bucket = storage_client.get_bucket(bucket_name)

# identify the files in the bucket
blob_list = list(bucket.list_blobs(prefix=prefix))
print('Output files:')
for blob in blob_list:
    print(blob.name)
    # json_string = blob.download_as_string()
    # response = json.loads(json_string)
    # for i in range(len(response['responses'])):
    #     if 'fullTextAnnotation' in response['responses'][i]:
    #         first_page_response = response['responses'][i]['fullTextAnnotation']['text']
    #         page_number = response['responses'][i]['context']['pageNumber']
    #         print(first_page_response)
    #         print("\nPage Number: " + str(page_number) + "\n")
    #     else:
    #         page_number = response['responses'][i]['context']['pageNumber']
    #         print("No text found")
    #         print("\nPage Number: " + str(page_number) + "\n")

# ################################################################
# # store in csv file
# import pandas as pd

# df = pd.DataFrame(columns=['Page Number', 'Text'])

# for blob in blob_list:
#     json_string = blob.download_as_string()
#     response = json.loads(json_string)
#     for i in range(len(response['responses'])):
#         if 'fullTextAnnotation' in response['responses'][i]:
#             first_page_response = response['responses'][i]['fullTextAnnotation']['text']
#             page_number = response['responses'][i]['context']['pageNumber']
#             # use df.concat() to append to the end of the dataframe
#             df = pd.concat([df, pd.DataFrame({'Page Number': page_number, 'Text': first_page_response}, index=[i])], ignore_index=True)
#         else:
#             page_number = response['responses'][i]['context']['pageNumber']
#             df = pd.concat([df, pd.DataFrame({'Page Number': page_number, 'Text': 'No text found'}, index=[i])], ignore_index=True)

# # sort the dataframe by page number
# df.sort_values(by='Page Number', inplace=True)
# df.reset_index(inplace=True, drop=True)

# # save the dataframe to csv file using gcs_list_selected_name
# df.to_csv('csv_out/' + gcs_list_selected_name + '.csv', index=False)
# ################################################################
# store in json file
import json

json_list = []

for blob in blob_list:
    json_string = blob.download_as_string()
    response = json.loads(json_string)
    for i in range(len(response['responses'])):
        if 'fullTextAnnotation' in response['responses'][i]:
            first_page_response = response['responses'][i]['fullTextAnnotation']['text']
            page_number = response['responses'][i]['context']['pageNumber']
            json_list.append({'page_number': page_number, 'text': first_page_response})
        else:
            page_number = response['responses'][i]['context']['pageNumber']
            json_list.append({'page_number': page_number, 'text': 'No text found'})

# sort the json list by page number
json_list.sort(key=lambda x:x['page_number'])

# save the json list to json file using gcs_list_selected_name
with open('json_out/' + gcs_list_selected_name + '.json', 'w') as f:
    json.dump(json_list, f)

# ################################################################
# store in sqlalchemy database
# from sqlalchemy import create_engine
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# engine = create_engine('sqlite:///test.db', echo=True)
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()

# class Text(Base):
#     __tablename__ = 'text'
#     id = Column(Integer, primary_key=True)
#     page_number = Column(Integer)
#     text = Column(String)

#     def __repr__(self):
#         return "<Text(page_number='%s', text='%s')>" % (self.page_number, self.text)

# Base.metadata.create_all(engine)

# for blob in blob_list:
#     json_string = blob.download_as_string()
#     response = json.loads(json_string)
#     for i in range((int(batch_size)-1)):
#         first_page_response = response['responses'][i]['fullTextAnnotation']['text']
#         page_number = response['responses'][i]['context']['pageNumber']
#         text = Text(page_number=page_number, text=first_page_response)
#         session.add(text)
#         session.commit()

##Retrieve the text from the sql database
# for instance in session.query(Text).order_by(Text.id):
#     print(instance.page_number, instance.text)
################################################################
