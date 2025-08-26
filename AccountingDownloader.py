import re
import logging
import os
import time
import requests
from typing import List, Dict
from pydantic import TypeAdapter

from helpers import Paginator, dump_to_file
from models.InfaktAccounting import InfaktSAFV7Entity, InfaktSAFV7Response, InfaktSAFV7EntityDetails
from models.InfaktAccounting import InfaktVATEUEntity, InfaktVATEUResponse, InfaktVATEUEntityDetails
from models.InfaktAccounting import InfaktBookEntity, InfaktBookResponse, InfaktBookEntityDetails
from models.InfaktAccounting import InfaktIncomeTaxEntity, InfaktIncomeTaxResponse, InfaktIncomeTaxEntityDetails
from models.InfaktAccounting import InfaktInsuranceResponse, InfaktInsuranceEntity, InfaktInsuranceEntityDetails

class AccountingDownloader():
  def __init__(self, logger: logging.Logger, infakt_session: requests.Session, infakt_domain: str):
    self.logger = logger
    self.infakt_session = infakt_session
    self.infakt_domain = infakt_domain

    # Create the required folder
    if not os.path.exists('data/accounting'): os.mkdir('data/accounting')

  async def download_accounting_data(self, category: str, base_endpoint_url: str, response_model, entity_model, entity_details_model) -> bool:
    dir_path: str = f'data/accounting/{category}'
    try:
      if not os.path.exists(dir_path): os.mkdir(dir_path)
      if not os.path.exists(f'{dir_path}/details'): os.mkdir(f'{dir_path}/details')
    except Exception as e:
      self.logger.error('Failed to create directories required for accounting data handling - %s', category)
      return False
    
    try:
      all_entities = []
      for data_result in Paginator(self.infakt_session, f'{base_endpoint_url}.json'):
        parsed_data = response_model.model_validate(data_result.json())
        if len(parsed_data.entities) == 0:
          break
        all_entities.extend(parsed_data.entities)

      # Sort the data in ascending order
      all_entities.sort(key=lambda x: x.period)

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

        target_name: str = f'{entity.period} {entity.id}'
        
        # Restore the path if already exists
        if entity.id in archived_entities_id and archived_entities_id[entity.id] != f'{target_name}.json':
          os.rename(f'{dir_path}/details/{archived_entities_id[entity.id]}', f'{dir_path}/details/{target_name}.json')

        parsed_entity_details = entity_details_model.model_validate(entity_details_result.json())
        
        # Save entity to file
        dump_to_file(f'{dir_path}/details/{target_name}.json', parsed_entity_details.model_dump_json(indent=2, exclude_none=True))
       
      # Adjust deleted data names
      deleted_entities_id = archived_entities_id.keys() - [entity.id for entity in all_entities]
      for deleted_entity_id in deleted_entities_id:
        target_name = f'(DELETED) {deleted_entity_id}'
        if archived_entities_id[deleted_entity_id] != target_name:
          os.rename(f'{dir_path}/details/{archived_entities_id[deleted_entity_id]}', f'{dir_path}/details/{target_name}.json')

      self.logger.info('Finished fetching accounting data - %s', category)
      return True
    except Exception as e:
      self.logger.error('Failed to handle accounting data - %s %s %s', category, type(e), e)
      return False

  async def download(self) -> bool:
    results: List[bool] = [
      await self.download_accounting_data('JPK', f'{self.infakt_domain}/api/v3/saf_v7_files', response_model=InfaktSAFV7Response, entity_model=InfaktSAFV7Entity, entity_details_model=InfaktSAFV7EntityDetails),
      await self.download_accounting_data('VAT_EU', f'{self.infakt_domain}/api/v3/vat_eu_taxes', response_model=InfaktVATEUResponse, entity_model=InfaktVATEUEntity, entity_details_model=InfaktVATEUEntityDetails),
      await self.download_accounting_data('REV_TAX', f'{self.infakt_domain}/api/v3/income_taxes', response_model=InfaktIncomeTaxResponse, entity_model=InfaktIncomeTaxEntity, entity_details_model=InfaktIncomeTaxEntityDetails),
      await self.download_accounting_data('KPiR', f'{self.infakt_domain}/api/v3/books', response_model=InfaktBookResponse, entity_model=InfaktBookEntity, entity_details_model=InfaktBookEntityDetails),
      await self.download_accounting_data('INSUR', f'{self.infakt_domain}/api/v3/insurance_fees', response_model=InfaktInsuranceResponse, entity_model=InfaktInsuranceEntity, entity_details_model=InfaktInsuranceEntityDetails)
    ]
    return all(results)