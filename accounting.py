import requests
import os
from dotenv import load_dotenv
import json
import urllib.request

load_dotenv()

API_KEY = os.getenv('INFAKT_API_KEY')

try:
  os.mkdir('data/accounting')
except Exception as e:
  pass

def download_accounting_data(type, endpoint):
  dir_path = f'data/accounting/{type}'
  try:
    os.mkdir(dir_path)
    os.mkdir(f'{dir_path}/details')
  except Exception as e:
    pass

  i = 0
  all_entities = []
  while True:
    list_result = requests.get(f'{endpoint}.json?limit=100&offset={i*100}', headers={
      "accept": "application/json",
      "X-inFakt-ApiKey": API_KEY
    })
    json_list_result = list_result.json()

    entities = json_list_result.get('entities')
    if len(entities) == 0:
      break
    for entity in entities:
      all_entities.append(entity)

    i += 1

  file = open(f'{dir_path}/list.json', "w+")
  file.write(json.dumps(all_entities, indent=2))
  file.close()

  for entity in all_entities:
    id = entity.get('id')
    detail_result = requests.get(f'{endpoint}/{id}.json', headers={
      "accept": "application/json",
      "X-inFakt-ApiKey": API_KEY
    })
    json_detail_result = detail_result.json()

    file = open(f'{dir_path}/details/{id}.json', "w+")
    file.write(json.dumps(json_detail_result, indent=2))
    file.close()
  
download_accounting_data('JPK', 'https://api.infakt.pl/api/v3/saf_v7_files')
download_accounting_data('VAT_EU', 'https://api.infakt.pl/api/v3/vat_eu_taxes')
download_accounting_data('REV_TAX', 'https://api.infakt.pl/api/v3/income_taxes')
download_accounting_data('KPiR', 'https://api.infakt.pl/api/v3/books')
download_accounting_data('INSUR', 'https://api.infakt.pl/api/v3/insurance_fees')