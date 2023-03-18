""" INSTRUCTIONS
2a. create a project on google cloud
2b. get google application credentials and store into your files, this/the project helps google to charge your account for your usage
2c. store pdf file that needs to be text extracted onto your google cloud storage folder (also called the bucket); for example below, I have my bucket named pdf_test_hs. This/gcs helps google to utilize their technology on your files.
2d. get the "gsutil URI"; click on the pdf file in your gcs, the hyperlink will take you to the pdf details page, within the detail table you will find the "gsutil URI"
2e. insert your gsutil URI into the gcs_list, if you replace the existing URI and only have one gsutil URI, then put gcs_list_selected = gcs_list[0]
2f. *** batch_size = 10; may run into issues if your 10 pages of text exceeds 10mb size, so decrease the size if necessary, but I don't think many pdf pages will have more than 10mb of pure texts...
RUN PYTHON FILE => GO TO STEP 3
"""
#Skip if json batch folder already created in bucket
#1 pdf page is a unit, 1000 unit free per month
#IN FUTURE: SORT THROUGH LIST OF PDF FILES IN GCS BUCKET THEN PROCESS SELECTED PDF FILES
import os # for file handling and image processing 
import re # re for regular expression 
from google.cloud import vision 
from google.cloud import storage 
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'credentials\ProjectName-XYZXYZ-XYZXYZXYZYXZYXZY.json' 

client = vision.ImageAnnotatorClient()

batch_size = 10 # The number of pages to process per batch. 
mime_type = 'application/pdf' 
feature = vision.Feature( type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION) 
''' 
gs://pdf_test_hs/the-autobiography-of-nelson-mandela.pdf 
gs://pdf_test_hs/Citation Correction.pdf 
gs://pdf_test_hs/PGE_document.pdf 
gs://pdf_test_hs/RENTCafe_LeaseAgreement_Executed (2).pdf 
'''

#INSTRUCTION: ADD NEW PDF FILE FROM GCS TO THE gcs_list
gcs_list = [ 'gs://pdf_test_hs/the-autobiography-of-nelson-mandela.pdf', 'gs://pdf_test_hs/Citation Correction.pdf', 'gs://pdf_test_hs/PGE_document.pdf', 'gs://pdf_test_hs/RENTCafe_LeaseAgreement_Executed (2).pdf']

#INSTRUCTION: SELCT THE PDF FILE BY CHANGING THE INDEX OF THE gcs_list_selected
gcs_list_selected = gcs_list[3]

#keep only the name of pdf from the uri
gcs_list_selected_name = gcs_list_selected.split('/')[-1].split('.')[0]

gcs_source_uri = gcs_list_selected
gcs_source = vision.GcsSource(uri=gcs_source_uri)
input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

gcs_destination_uri = gcs_list_selected.replace('.pdf', '_output/')
gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
output_config = vision.OutputConfig( gcs_destination=gcs_destination, batch_size=batch_size)

async_request = vision.AsyncAnnotateFileRequest( features=[feature], input_config=input_config, output_config=output_config)

operation = client.async_batch_annotate_files(requests=[async_request]) 
print('Waiting for the operation to finish.') 
operation.result(timeout=420)

