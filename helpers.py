import requests
import time
import re
from typing import TypeVar
from io import BytesIO
from pypdf import PdfReader, PdfWriter

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
    # TODO: Add retrying
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

def dump_to_file(path: str, content: str | bytes):
  if isinstance(content, bytes):
    content = content.decode()
  file = open(path, 'w+', encoding='utf-8')
  file.write(content)
  file.close()

def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
  writer = PdfWriter()

  for pdf_bytes in pdf_bytes_list:
    reader = PdfReader(BytesIO(pdf_bytes))
    for page in reader.pages:
      writer.add_page(page)

  output_stream = BytesIO()
  writer.write(output_stream)
  return output_stream.getvalue()

UUID_REGEX = re.compile(r'\b' + '-'.join([rf'[0-9a-fA-F]{x}' for x in [8, 4, 4, 4, 12]]) + r'\b')