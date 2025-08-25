from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Optional, List
from pydantic import BaseModel, field_validator
from models.InfaktPaginateResponseMetainfo import InfaktPaginateResponseMetainfo

class InfaktCostEntitySource(str, Enum):
  INFAKT = 'infakt'

class InfaktCostStatusSymbol(str, Enum):
  ACCOUNTED = 'accounted'
  COST_ACCOUNTED = 'cost_accounted'
  AUTOX_ACCOUNTED = 'autox_accounted'
  COST_REJECTED = 'cost_rejected'
  TO_CLARIFY = 'to_clarify'
  COST_NOT_ACCOUNTED = 'cost_not_accounted'
  COST_ACCOUNTING_NOT_APPLICABLE = 'cost_accounting_not_applicable'
  
  MERIT_UNSENT = 'merit_unsent'

  CLIENT_SENDING_NOT_APPLICABLE = 'client_sending_not_applicable'

  KSEF_SENDING_NOT_APPLICABLE = 'ksef_sending_not_applicable'

  PDF_NOT_DOWNLOADED = 'pdf_not_downloaded'

  XML_DOWNLOAD_NOT_APPLICABLE = 'xml_download_not_applicable'

  PAID = 'paid'
  UNPAID = 'unpaid'
  PARTIAL_PAYMENT = 'partial_payment'
  PAYMENT_NOT_APPLICABLE = 'payment_not_applicable'

class InfaktCostStatusGroup(str, Enum):
  COST_ACCOUNTING = 'cost_accounting'
  ACCOUNTING = 'accounting'
  PAYMENT = 'payment'
  MERIT_SENDING = 'merit_sending'
  CLIENT_SENDING = 'client_sending'
  KSEF_SENDING = 'ksef_sending'
  PDF_DOWNLOAD = 'pdf_download'
  XML_DOWNLOAD = 'xml_download'

class InfaktCostStatus(BaseModel, extra='forbid'):
  symbol: InfaktCostStatusSymbol
  name: str
  group: InfaktCostStatusGroup

class InfaktCostNoteKind(str, Enum):
  REJECTED_REASON = 'rejected_reason'
  AUTOX_REJECTED_DUPLICATED_COST = 'autox_rejected_duplicated_cost'
  AUTOX_REJECTED = 'autox_rejected'

class InfaktCostNote(BaseModel, extra='forbid'):
  kind: InfaktCostNoteKind
  content: str
  created_by: Optional[str] # UUID
  author_first_name: Optional[str]
  author_last_name: Optional[str]
  author_avatar: Optional[str] # URL
  created_at: datetime

class InfaktCostKind(str, Enum):
  COST = 'cost'
  DOCUMENT_SCAN = 'document_scan'
  INTERNAL_EVIDENCE = 'internal_evidence'
  WORK_FUND_EVIDENCE = 'work_fund_evidence'
  HEALTH_FEE_EVIDENCE = 'health_fee_evidence'

class InfaktCostEntity(BaseModel, extra='forbid'):
  uuid: str
  number: str
  net_price: Optional[int]
  gross_price: Optional[int]
  tax_price: Optional[int]
  currency: Optional[str]
  accounted_at: Optional[date]
  issue_date: Optional[date]
  received_date: Optional[date]
  due_date: Optional[date]
  seller_name: Optional[str]
  seller_tax_code: Optional[str]
  seller_bank_account: Optional[str]
  description: Optional[str]
  added_by: str
  category: Optional[str]
  kind: InfaktCostKind
  notes_count: int
  newest_note: Optional[InfaktCostNote]
  duplicated: bool
  created_at: datetime # 2022-09-26 11:28:57 +0200
  source: Optional[InfaktCostEntitySource]
  reconciliation_id: Optional[None]
  statuses: List[InfaktCostStatus]

  @field_validator('created_at', mode='before')
  @classmethod
  def parse_custom_created_at(cls, value):
    if isinstance(value, datetime): return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z')
  
class InfaktCostAttachmentKind(IntEnum): # ???
  INVOICE = 21
  CUSTOM = 20
  EVIDENCE = 23

class InfaktCostAttachment(BaseModel, extra='forbid'):
  kind_id: InfaktCostAttachmentKind
  file_name: str
  document_scan_uuid: str
  file_url: str
  download_url: str

class InfaktCostRelatedInternalNote(BaseModel, extra='forbid'):
  number: str
  url: str

class InfaktCostEntityDetailed(InfaktCostEntity):
  attachments: List[InfaktCostAttachment]
  related_internal_note: Optional[InfaktCostRelatedInternalNote]
  notes: List[InfaktCostNote]
  related_exchange_differences_internal_evidences: Optional[List[None]] # ???

class InfaktCostsResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktCostEntity]
