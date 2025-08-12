import requests
import os
from dotenv import load_dotenv
import json
import urllib.request

load_dotenv()

API_KEY = os.getenv('INFAKT_API_KEY')

try:
  os.mkdir('data/account')
except Exception as e:
  pass

acc_result = requests.get(f'https://api.infakt.pl/api/v3/account/details.json', headers={
    "accept": "application/json",
    "X-inFakt-ApiKey": API_KEY
})
json_acc_result = acc_result.json()

file = open('data/account/data.json', "w+")
file.write(json.dumps(json_acc_result, indent=2))
file.close()

events = []
i = 0
while True:
  result = requests.get(f'https://api.infakt.pl/api/v3/account/activities.json?limit=100&offset={i*100}', headers={
      "accept": "application/json",
      "X-inFakt-ApiKey": API_KEY
  })

  json_result = result.json()
  entities = json_result.get('entities')
  if len(entities) == 0:
    break
  for entity in entities:
    events.append(entity)

  i += 1

file = open('data/account/events.json', "w+")
file.write(json.dumps(events, indent=2))
file.close()