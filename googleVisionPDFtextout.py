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
