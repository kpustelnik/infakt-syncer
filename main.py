import asyncio
import logging
from logging.handlers import RotatingFileHandler
import sys
import requests
import json
import os
import time
import urllib
from io import BytesIO
from dotenv import load_dotenv
from pypaperless import Paperless
from pypaperless.models.common import TaskStatusType
from git import Repo
from datetime import datetime
from typing import List

from helpers import Paginator, merge_pdfs
from models.InfaktCosts import InfaktCostsResponse, InfaktCostEntityDetailed
from AccountDetailsDownloader import AccountDetailsDownloader
from AccountingDownloader import AccountingDownloader
from InvoicesDownloader import InvoicesDownloader
from CostsUploader import CostsUploader

load_dotenv() # Load the dotenv

# Setup the logger
logger = logging.getLogger("log")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"))
file_handler = RotatingFileHandler(
  'logs/usage.log',
  maxBytes=25*1024*1024,
  backupCount=5
)
file_handler.setFormatter(logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"))
logger.addHandler(handler)
logger.addHandler(file_handler)

# Init paperless
paperless = None
if os.getenv('PAPERLESS_URL') is not None and os.getenv('PAPERLESS_TOKEN') is not None:
  paperless = Paperless(
    url=os.getenv('PAPERLESS_URL'),
    token=os.getenv('PAPERLESS_TOKEN')
  )
else:
  logger.info('Not setting up paperless due to lack of credentials.')

# Set up InFakt session
infakt_session = requests.Session()
infakt_session.headers.update({
  "X-inFakt-ApiKey": os.getenv('INFAKT_API_KEY')
})
infakt_domain = os.getenv('INFAKT_API_DOMAIN') or 'https://api.infakt.pl'

# Prepare the data folder
if not os.path.exists('data'):
  os.mkdir('data')
# Init the git repo
data_repo: Repo = Repo.init('data')

async def main():
  if paperless is not None: await paperless.initialize()

  results: List[bool] = [
    await CostsUploader(logger, infakt_session, infakt_domain, paperless).process(),
    await AccountDetailsDownloader(logger, infakt_session, infakt_domain, paperless).process(),
    await AccountingDownloader(logger, infakt_session, infakt_domain, paperless).process(),
    await InvoicesDownloader(logger, infakt_session, infakt_domain, paperless).process()
  ]
  all_success = all(results)

  if paperless is not None: await paperless.close()

  # Stage all the changes
  data_repo.git.add(A=True)
  data_repo.index.commit(
    message='Syncing InFakt at %s - %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S %z'), 'SUCCESS' if all_success else 'ERROR')
  )

    return
    # Syncing the documents from paperless to InFakt
    to_upload_infakt_tag = await paperless.tags(6)
    async for document in paperless.documents.search(f'tag:"{to_upload_infakt_tag.name}"'):
      document.tags.remove(to_upload_infakt_tag.id) # Remove the tag
      await document.update()

      content = await document.get_download()
      print("Got content", type(content.content))
      
      upload_result = infakt_session.post(
        'https://api.sandbox-infakt.pl/api/v3/documents/costs/upload.json',
        data={},
        files=[
          (
            "uploads[]",
            (content.disposition_filename, BytesIO(content.content), 'application/octet-stream')
          )
        ]
      )

      print(upload_result)
      print(upload_result.json())

      print(InfaktUploadResponse.model_validate(upload_result.json()))

    return

    for costs_result in Paginator(infakt_session, 'https://api.infakt.pl/api/v3/documents/costs.json'):
      parsed_costs: InfaktCostsResponse = InfaktCostsResponse.model_validate(costs_result.json())

      if len(parsed_costs.entities) == 0:
        break

      i = 0
      for cost in parsed_costs.entities:
        i += 1
        if i == 11:
          return # Up to 3 docs

        cost_details_result = infakt_session.get(f'https://api.infakt.pl/api/v3/documents/costs/{cost.uuid}.json', headers={
          "accept": "application/json"
        }) # TODO: Also handle ratelimits

        parsed_cost_details = InfaktCostEntityDetailed.model_validate(cost_details_result.json())

        attachments = []
        for attachment_data in parsed_cost_details.attachments:
          attachment_content = urllib.request.urlopen(attachment_data.download_url).read()
          attachments.append(attachment_content)
        merged_attachments = merge_pdfs(attachments) if len(attachments) > 1 else attachments[0]

        infakt_uuid_field = await paperless.custom_fields(1)
        doc_uuid_field_value = infakt_uuid_field.draft_value(cost.uuid)

        doc = paperless.documents.draft(
          document=merged_attachments,
          title=f'Test document infakt {cost.uuid}',
          filename=f'{cost.uuid}.pdf',
          created=cost.created_at,
          tags=[2, 5] # Infakt Faktura ID (Tag Dokumenty firmowe; to do)
        )

        task_id = await doc.save()
        task = await paperless.tasks(task_id)
        while task.status in [TaskStatusType.PENDING, TaskStatusType.STARTED]:
          time.sleep(2)
          await task.load()
        
        if task.status == TaskStatusType.SUCCESS:
          print("Success!", task.related_document)
          saved_doc = await paperless.documents(task.related_document)
          saved_doc.custom_fields += doc_uuid_field_value
          saved_doc.document_type = 12 # Infakt Faktura Kosztowa
          await saved_doc.update()

          note_draft = saved_doc.notes.draft()
          note_draft.note = json.dumps(json.loads(parsed_cost_details.model_dump_json()), indent=2)
          await note_draft.save()
        elif task.status == TaskStatusType.FAILURE:
          print("Failure!", task.related_document)

          #file_path = f'{dir_path}/attachments/{attachment_data.get("file_name")}'
          #if not os.path.isfile(file_path):
          #  urllib.request.urlretrieve(attachment_data.get("download_url"), file_path)
          # Setting file_url and download_url to null as it always changes
          #attachment_data.pop('download_url')
          #attachment_data.pop('file_url')


        '''     
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


        file = open(f'{dir_path}/detailed_data.json', "w+")
        file.write(json.dumps(json_detail_result, indent=2))
        file.close()
        '''

asyncio.run(main())
