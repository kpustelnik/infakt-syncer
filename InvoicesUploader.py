import logging
import time
import requests
from pypaperless import Paperless
from typing import Optional
from io import BytesIO

from models.InfaktUpload import InfaktUploadResponse, InfaktUploadEntity

# Syncing the documents from Paperless-ngx to InFakt
class InvoicesUploader():
  def __init__(self, logger: logging.Logger, infakt_session: requests.Session, infakt_domain: str, paperless: Optional[Paperless]):
    self.logger = logger
    self.infakt_session = infakt_session
    self.infakt_domain = infakt_domain
    self.paperless = paperless

  async def process(self) -> bool:
    if self.paperless is None:
      self.logger.warning('Skipping invoice uploading as Paperless is not connected')
      return True
    
    try:
      all_success: bool = True

      # TODO: Custom ids
      to_upload_infakt_tag = await self.paperless.tags(6) # Fetch the TO UPLOAD tag
      infakt_scan_uuid_field = await self.paperless.custom_fields(3) # Custom field to store the document scan UUID
      async for document in self.paperless.documents.search(f'tag:"{to_upload_infakt_tag.name}"'): # Look up all the documents
        try:
          self.logger.info('Uploading %s (ID: %d) to InFakt', document.original_file_name, document.id)

          # Fetch the document content (binary source)
          document_content = await document.get_download()

          attempt: int = 0
          while True:
            attempt += 1
            if attempt > 3:
              raise Exception('Exceeded maximum fetch attempts')

            upload_result = self.infakt_session.post(
              'https://api.infakt.pl/api/v3/documents/costs/upload.json',
              data={},
              files=[
                (
                  "uploads[]",
                  (document_content.disposition_filename, BytesIO(document_content.content), 'application/octet-stream')
                )
              ]
            )
            if upload_result.status_code == 201:
              break # Fetched uploaded
            elif upload_result.status_code == 429: # Ratelimited
              retryAfter = upload_result.headers['Retry-After']
              if retryAfter is not None:
                self.logger.warning(f'Rate limited - waiting {retryAfter} seconds')
                time.sleep(retryAfter)
            else:
              self.logger.warning(f'Received {upload_result.status_code} error - retrying in 1s')
              time.sleep(1)

          parsed_upload_result: InfaktUploadResponse = InfaktUploadResponse.model_validate(upload_result.json())
          if len(parsed_upload_result.entities) != 1:
            raise Exception('Incorrect amount of result entities')
          
          uploaded_document_data: InfaktUploadEntity = parsed_upload_result.entities[0]

          # Add the Document Scan UUID field
          doc_uuid_field_value = infakt_scan_uuid_field.draft_value(uploaded_document_data.document_scan_uuid)
          document.custom_fields += doc_uuid_field_value

          # Remove the TO UPLOAD tag
          document.tags.remove(to_upload_infakt_tag.id)

          update_result: bool = await document.update()
          if not update_result:
            raise Exception("Failed to update the document")

        except Exception as e:
          self.logger.error('Failed to upload the invoice - %s %s', type(e), e)
          all_success = False

      return all_success
    except Exception as e:
      self.logger.error('Failed to upload the invoices - %s %s', type(e), e)
      return False