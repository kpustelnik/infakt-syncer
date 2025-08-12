import requests
import os
from dotenv import load_dotenv
import json
import urllib.request

load_dotenv()

API_KEY = os.getenv('INFAKT_API_KEY')

try:
  os.mkdir('data/costs')
except Exception as e:
  pass

i = 0
while True:
  result = requests.get(f'https://api.infakt.pl/api/v3/documents/costs.json?limit=100&offset={i*100}', headers={
      "accept": "application/json",
      "X-inFakt-ApiKey": API_KEY
  })
  json_result = result.json()
  
  entities = json_result.get('entities')
  if len(entities) == 0:
    break
  for entity in entities:
    uuid = entity.get("uuid")
    detail_result = requests.get(f'https://api.infakt.pl/api/v3/documents/costs/{uuid}.json', headers={
      "accept": "application/json",
      "X-inFakt-ApiKey": API_KEY
    })
    json_detail_result = detail_result.json()

    isRejected = False
    for status in json_detail_result.get('statuses'):
      if status.get('symbol') == "cost_rejected":
        isRejected = True
        break

    dir_path = f'data/costs/{entity.get("issue_date")} - {uuid}'
    if isRejected:
      dir_path += ' (REJECTED)'

    try:
      os.mkdir(dir_path)
    except Exception as e:
      pass
    
    file = open(f'{dir_path}/data.json', "w+")
    file.write(json.dumps(entity, indent=2))
    file.close()

    try:
      os.mkdir(f'{dir_path}/attachments')
    except Exception as e:
      pass

    for attachment_data in json_detail_result.get('attachments'):
      file_path = f'{dir_path}/attachments/{attachment_data.get("file_name")}'
      if not os.path.isfile(file_path):
        urllib.request.urlretrieve(attachment_data.get("download_url"), file_path)
      # Setting file_url and download_url to null as it always changes
      attachment_data.pop('download_url')
      attachment_data.pop('file_url')

    file = open(f'{dir_path}/detailed_data.json', "w+")
    file.write(json.dumps(json_detail_result, indent=2))
    file.close()

  i += 1