import requests
import time
from typing import TypeVar, Callable

T = TypeVar('T')

class Paginator():
  def __init__(self, session: requests.Session, url: str, limit: int = 100):
    self.url = url
    self.limit = limit
    self.session = session
  
  def __iter__(self):
    self.offset_cnt = 0
    return self

  def __next__(self):
    results = self.session.get(f'{self.url}?limit={self.limit}&offset={self.offset_cnt * self.limit}', headers={
      "accept": "application/json"
    })
    if results.status_code == 429:
      retryAfter = results.headers['Retry-After']
      if retryAfter is not None:
        print(f"Rate limited. Sleeping {retryAfter} seconds")
        time.sleep(int(retryAfter))
      
    self.offset_cnt += 1
    
    return results

def dump_to_file(path: str, content: str):
  file = open(path, 'w+')
  file.write(content)
  file.close()