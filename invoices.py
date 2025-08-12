import requests
import os
from dotenv import load_dotenv
import json
import urllib.request

load_dotenv()

API_KEY = os.getenv('INFAKT_API_KEY')

try:
  os.mkdir('data/invoices')
except Exception as e:
  pass

def download_invoice_data(type, endpoint, download_available=False, attachments_available=False):
  dir_path = f'data/invoices/{type}'
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
    uuid = entity.get('uuid')

    if download_available or attachments_available:
      try:
        os.mkdir(f'{dir_path}/details/{uuid}')
      except Exception as e:
        pass

    detail_result = requests.get(f'{endpoint}/{uuid}.json', headers={
      "accept": "application/json",
      "X-inFakt-ApiKey": API_KEY
    })
    json_detail_result = detail_result.json()

    file = open(f'{dir_path}/details/{uuid}/details.json' if download_available or attachments_available else f'{dir_path}/details/{uuid}.json', "w+")
    file.write(json.dumps(json_detail_result, indent=2))
    file.close()

    if attachments_available:
      try:
        os.mkdir(f'{dir_path}/details/{uuid}/attachments')
      except Exception as e:
        pass

      attachments_result = requests.get(f'{endpoint}/{uuid}/attachments.json', headers={
        "accept": "application/json",
        "X-inFakt-ApiKey": API_KEY
      })
      json_attachments_result = attachments_result.json()

      attachments_entities = json_attachments_result.get('entities')
      for attachment_data in attachments_entities:
        file_path = f'{dir_path}/details/{uuid}/attachments/{attachment_data.get("name")}'
        if not os.path.isfile(file_path):
          urllib.request.urlretrieve(attachment_data.get("download_link"), file_path)
        # Setting download_link to null as it always changes
        attachment_data.pop('download_link')

      file = open(f'{dir_path}/details/{uuid}/attachments.json', "w+")
      file.write(json.dumps(attachments_entities, indent=2))
      file.close()

download_invoice_data('DAILY_REV', 'https://api.infakt.pl/api/v3/daily_revenues')
download_invoice_data('INT_EVI', 'https://api.infakt.pl/api/v3/internal_evidences')
download_invoice_data('FISC_REP', 'https://api.infakt.pl/api/v3/fiscal_reports')
download_invoice_data('INT_INV', 'https://api.infakt.pl/api/v3/internal_invoices')
download_invoice_data('OSS_CORR_INV', 'https://api.infakt.pl/api/v3/corrective_oss_invoices')
download_invoice_data('OSS_INV', 'https://api.infakt.pl/api/v3/oss_invoices') # TODO: Downloading
download_invoice_data('FINAL_INV', 'https://api.infakt.pl/api/v3/final_invoices') # TODO: Downloading
download_invoice_data('ADV_INV', 'https://api.infakt.pl/api/v3/advance_invoices') # TODO: Downloading
download_invoice_data('MARG_INV', 'https://api.infakt.pl/api/v3/margin_invoices') # TODO: Downloading
download_invoice_data('CORR_INV', 'https://api.infakt.pl/api/v3/corrective_invoices') # TODO: Downloading
download_invoice_data('INV', 'https://api.infakt.pl/api/v3/invoices', attachments_available=True)