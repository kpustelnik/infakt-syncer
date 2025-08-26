import logging
import os
import time
import requests
import re
from typing import List, Dict
from pydantic import TypeAdapter
from pypaperless import Paperless

from helpers import Paginator, dump_to_file
from models.InfaktAccountEvents import InfaktAccountEvent, InfaktAccountEventsResponse, InfaktAccountEventsIgnoreFields
from models.InfaktAccountDetails import InfaktAccountDetails, InfaktAccountDetailsIgnoreFields
from models.InfaktAccountDetails import InfaktClientEntity, InfaktClientsResponse, InfaktClientEntityDetails
from models.InfaktAccountDetails import InfaktProductEntity, InfaktProductsResponse, InfaktProductEntityDetails
from models.InfaktAccountDetails import InfaktBankAccountEntity, InfaktBankAccountsResponse, InfaktBankAccountEntityDetails

class AccountDetailsDownloader():
  def __init__(self, logger: logging.Logger, infakt_session: requests.Session, infakt_domain: str, paperless: Paperless):
    self.logger = logger
    self.infakt_session = infakt_session
    self.infakt_domain = infakt_domain
    self.paperless = paperless

    # Create the required folder
    if not os.path.exists('data/account'): os.mkdir('data/account')

  async def download_account_details(self) -> bool:
    try:
      attempt: int = 0
      while True:
        attempt += 1
        if attempt > 3:
          raise Exception('Exceeded maximum fetch attempts')

        account_details_result = self.infakt_session.get(f'{self.infakt_domain}/api/v3/account/details.json', headers={
          "accept": "application/json"
        })
        if account_details_result.status_code == 200:
          break # Fetched successfully
        elif account_details_result.status_code == 429: # Ratelimited
          retryAfter = account_details_result.headers['Retry-After']
          if retryAfter is not None:
            self.logger.warning(f'Rate limited - waiting {retryAfter} seconds')
            time.sleep(retryAfter)
        else:
          self.logger.warning(f'Received {account_details_result.status_code} error - retrying in 1s')
          time.sleep(1)
      
      parsed_account_details: InfaktAccountDetails = InfaktAccountDetails.model_validate(account_details_result.json())
      
      # Save to file
      dump_to_file('data/account/details.json', parsed_account_details.model_dump_json(indent=2, exclude=InfaktAccountDetailsIgnoreFields, exclude_none=True))

      self.logger.info('Finished fetching account details')
      return True
    except Exception as e:
      self.logger.error('Failed to handle account details - %s %s', type(e), e)
      return False
    
  async def download_account_events(self) -> bool:
    try:
      all_events: List[InfaktAccountEvent] = []
    
      for events_result in Paginator(self.infakt_session, f'{self.infakt_domain}/api/v3/account/activities.json'):
        parsed_events: InfaktAccountEventsResponse = InfaktAccountEventsResponse.model_validate(events_result.json())
        if len(parsed_events.entities) == 0:
          break
        all_events.extend(parsed_events.entities)

      # Sort the events in ascending order
      all_events.sort(key=lambda x: x.performed_at)

      # Save to file
      dump_to_file('data/account/events.json', TypeAdapter(List[InfaktAccountEvent]).dump_json(all_events, indent=2, exclude=InfaktAccountEventsIgnoreFields, exclude_none=True))
      
      self.logger.info('Finished fetching account events')
      return True
    except Exception as e:
      self.logger.error('Failed to handle account events - %s %s', type(e), e)
      return False
    
  async def download_listed_data(self, category: str, base_endpoint_url: str, response_model, entity_model, entity_details_model) -> bool:
    dir_path: str = f'data/account/{category}'
    try:
      if not os.path.exists(dir_path): os.mkdir(dir_path)
      if not os.path.exists(f'{dir_path}/details'): os.mkdir(f'{dir_path}/details')
    except Exception as e:
      self.logger.error('Failed to create directories required for account data handling - %s', category)
      return False
    
    try:
      all_entities = []
      for data_result in Paginator(self.infakt_session, f'{base_endpoint_url}.json'):
        parsed_data = response_model.model_validate(data_result.json())
        if len(parsed_data.entities) == 0:
          break
        all_entities.extend(parsed_data.entities)

      # Sort the data in ascending order basing on id
      all_entities.sort(key=lambda x: x.id)

      # Save the entities list
      dump_to_file(f'{dir_path}/list.json', TypeAdapter(List[entity_model]).dump_json(all_entities, indent=2, exclude_none=True))
  
      entity_id_regex = re.compile(r'\b(\d+)\.')
      archived_entities_id: Dict[int, str] = { int(result.group(1)): x for x in os.listdir(f'{dir_path}/details') if (result := entity_id_regex.search(x)) is not None }

      for entity in all_entities:
        attempt: int = 0
        while True:
          attempt += 1
          if attempt > 3:
            raise Exception('Exceeded maximum fetch attempts')

          entity_details_result = self.infakt_session.get(f'{base_endpoint_url}/{entity.id}.json', headers={
            "accept": "application/json"
          })
          if entity_details_result.status_code == 200:
            break # Fetched successfully
          elif entity_details_result.status_code == 429: # Ratelimited
            retryAfter = entity_details_result.headers['Retry-After']
            if retryAfter is not None:
              self.logger.warning(f'Rate limited - waiting {retryAfter} seconds')
              time.sleep(retryAfter)
          else:
            self.logger.warning(f'Received {entity_details_result.status_code} error - retrying in 1s')
            time.sleep(1)

        parsed_entity_details = entity_details_model.model_validate(entity_details_result.json())
        target_name: str = f'{entity.id}'
        
        # Restore the path if already exists
        if entity.id in archived_entities_id and archived_entities_id[entity.id] != f'{target_name}.json':
          os.rename(f'{dir_path}/details/{archived_entities_id[entity.id]}', f'{dir_path}/details/{target_name}.json')

        # Save entity to file
        dump_to_file(f'{dir_path}/details/{target_name}.json', parsed_entity_details.model_dump_json(indent=2, exclude_none=True))
       
      # Adjust deleted data names
      deleted_entities_id = archived_entities_id.keys() - [entity.id for entity in all_entities]
      for deleted_entity_id in deleted_entities_id:
        target_name: str = f'(DELETED) {deleted_entity_id}'
        if archived_entities_id[deleted_entity_id] != target_name:
          os.rename(f'{dir_path}/details/{archived_entities_id[deleted_entity_id]}', f'{dir_path}/details/{target_name}.json')

      self.logger.info('Finished fetching account data - %s', category)
      return True
    except Exception as e:
      self.logger.error('Failed to handle account data - %s %s %s', category, type(e), e)
      return False

  async def process(self) -> bool:
    results: List[bool] = [
      await self.download_account_details(),
      await self.download_account_events(),
      await self.download_listed_data('PRODUCTS', f'{self.infakt_domain}/api/v3/products', entity_model=InfaktProductEntity, response_model=InfaktProductsResponse, entity_details_model=InfaktProductEntityDetails),
      await self.download_listed_data('BANK_ACCOUNTS', f'{self.infakt_domain}/api/v3/bank_accounts', entity_model=InfaktBankAccountEntity, response_model=InfaktBankAccountsResponse, entity_details_model=InfaktBankAccountEntityDetails),
      await self.download_listed_data('CLIENTS', f'{self.infakt_domain}/api/v3/clients', entity_model=InfaktClientEntity, response_model=InfaktClientsResponse, entity_details_model=InfaktClientEntityDetails)
    ]
    return all(results)