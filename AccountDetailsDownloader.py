import logging
import os
import time
import requests
from typing import List
from pydantic import TypeAdapter

from helpers import Paginator, dump_to_file
from models.InfaktAccountEvents import InfaktAccountEvent, InfaktAccountEventsResponse, InfaktAccountEventsIgnoreFields
from models.InfaktAccountDetails import InfaktAccountDetails, InfaktAccountDetailsIgnoreFields

class AccountDetailsDownloader():
  def __init__(self, logger: logging.Logger, infakt_session: requests.Session):
    self.logger = logger
    self.infakt_session = infakt_session

    # Create the required folder
    if not os.path.exists('data/account'): os.mkdir('data/account')

  async def download_account_details(self) -> bool:
    try:
      attempt: int = 0
      while True:
        attempt += 1
        if attempt >= 3:
          raise Exception('Exceeded maximum fetch attempts')

        account_details_result = self.infakt_session.get(f'https://api.infakt.pl/api/v3/account/details.json', headers={
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
    
      for events_result in Paginator(self.infakt_session, 'https://api.infakt.pl/api/v3/account/activities.json'):
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

  async def download(self):
    await self.download_account_details()
    await self.download_account_events()