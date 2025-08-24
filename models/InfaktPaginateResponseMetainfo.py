from pydantic import BaseModel

class InfaktPaginateResponseMetainfo(BaseModel):
  count: int
  total_count: int
  next: str
  previous: str