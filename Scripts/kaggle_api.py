# import os
# import json
#
# # Load Kaggle API key from the kaggle.json file
# with open(r'C:\Users\avisa\.kaggle\kaggle.json') as f:
#     kaggle_config = json.load(f)
#
# # Add the key to the header
# headers = {
#     'Authorization': f"Bearer {kaggle_config['key']}"
# }
#
# print(headers)

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

a = api.datasets_list()
for i in a:
    print(i)

