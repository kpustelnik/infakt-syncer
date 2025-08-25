from pydantic import BaseModel
from typing import List

class InfaktUploadEntity(BaseModel, extra='forbid'):
  success: bool
  name: str
  document_scan_uuid: str
  download_url: str

class InfaktUploadResponse(BaseModel, extra='forbid'):
  entities: List[InfaktUploadEntity]
