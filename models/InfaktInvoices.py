from pydantic import BaseModel, field_validator
from typing import List, Optional
from pydantic_extra_types.currency_code import Currency
from pydantic_extra_types.country import CountryAlpha2
from enum import Enum
from datetime import date as ddate, datetime

from models.InfaktPaginateResponseMetainfo import InfaktPaginateResponseMetainfo

class InfaktInvoiceEntityStatus(str, Enum):
  DRAFT = 'draft'
  PAID = 'paid'

class InfaktInvoiceEntityPaymentMethod(str, Enum):
  TRANSFER = 'transfer'
  CASH = 'cash'

class InfaktInvoiceEntityBusinessActivityKind(str, Enum):
  PRIVATE_PERSON = 'private_person'
  OTHER_BUSINESS = 'other_business'
  SELF_EMPLOYED = 'self_employed'

class InfaktInvoiceEntitySaleDateKind(str, Enum):
  SALE_DATE = 'sale_date'
  
class InfaktInvoiceEntityInvoiceDateKind(str, Enum):
  SALE_DATE = 'sale_date'

class InfaktInvoiceEntitySaleType(str, Enum):
  SERVICE = 'service'
  NONE = ''

class InfaktInvoiceEntitySalesKind(str, Enum):
  SPRZEDAZ_PODSTAWOWA = 'sprzedaz_podstawowa'

class InfaktInvoiceEntityVatExchangeDateKind(str, Enum):
  VAT = 'vat'

class InfaktInvoiceEntityExtensionPayments(BaseModel, extra='forbid'):
  available: bool
  link: Optional[str] = None

class InfaktInvoiceEntityExtensionShares(BaseModel, extra='forbid'):
  available: bool
  link: Optional[str] = None
  valid_until: Optional[None] = None # TODO

class InfaktInvoiceEntityExtensions(BaseModel, extra='forbid'):
  payments: InfaktInvoiceEntityExtensionPayments
  shares: InfaktInvoiceEntityExtensionShares

class InfaktInvoiceEntityKsefDataInvoiceKind(str, Enum):
  VAT = 'vat'
  MARGIN = 'margin'
  CORRECTIVE_INVOICE = 'corrective_invoice'
  ADVANCE = 'advance'

class InfaktInvoiceEntityKsefDataStatus(str, Enum):
  SUCCESS = 'success'

class InfaktInvoiceEntityKsefDataTimestamps(BaseModel, extra='forbid'):
  request_created_at: datetime
  request_finished_at: datetime

  @field_validator('request_created_at', mode='before')
  @classmethod
  def parse_custom_request_created_at(cls, value):
    if isinstance(value, datetime): return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z')
  
  @field_validator('request_finished_at', mode='before')
  @classmethod
  def parse_custom_request_finished_at(cls, value):
    if isinstance(value, datetime): return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z')

class InfaktInvoiceEntityKsefData(BaseModel, extra='forbid'):
  request_uuid: str
  invoice_uuid: str
  invoice_kind: InfaktInvoiceEntityKsefDataInvoiceKind
  ksef_number: str
  status: InfaktInvoiceEntityKsefDataStatus
  status_description: str
  timestamps: InfaktInvoiceEntityKsefDataTimestamps

# Invoice

class InfaktInvoiceKind(str, Enum):
  VAT = 'vat'
  INTERNAL = 'internal'

class InfaktInvoiceService(BaseModel, extra='forbid'):
  id: int
  name: str
  tax_symbol: str
  unit: str
  quantity: int
  unit_net_price: int
  net_price: int
  gross_price: int
  tax_price: int
  symbol: str
  pkwiu: Optional[str] = None
  cn: Optional[str] = None
  pkob: Optional[str] = None
  flat_rate_tax_symbol: Optional[str] = None
  discount: str
  unit_net_price_before_discount: int
  gtu_id: Optional[str] = None # TODO: Confirm type
  related_id: Optional[int] = None # TODO: Confirm type

class InfaktInvoiceEntityShared(BaseModel, extra='forbid'):
  id: int
  uuid: str
  parent_id: Optional[None] = None # TODO: Confirm type
  number: str
  currency: Currency
  paid_price: int
  notes: str
  kind: InfaktInvoiceKind
  payment_method: InfaktInvoiceEntityPaymentMethod
  split_payment: bool
  split_payment_type: Optional[None] = None # TODO
  recipient_signature: str
  seller_signature: str
  invoice_date: ddate
  sale_date: ddate
  vat_date_value: InfaktInvoiceEntityInvoiceDateKind
  continuous_service_start_on: Optional[None] = None # TODO
  continuous_service_end_on: Optional[None] = None # TODO
  occasional_sale: bool
  status: InfaktInvoiceEntityStatus
  payment_date: ddate
  paid_date: Optional[ddate] = None
  net_price: int
  tax_price: int
  gross_price: int
  left_to_pay: int
  client_id: Optional[int] = None
  client_uuid: Optional[str] = None
  client_company_name: Optional[str] = None
  client_first_name: Optional[str] = None
  client_last_name: Optional[str] = None
  client_business_activity_kind: Optional[InfaktInvoiceEntityBusinessActivityKind] = None
  client_street: Optional[str] = None
  client_street_number: Optional[str] = None
  client_flat_number: Optional[str] = None
  client_city: Optional[str] = None
  client_post_code: Optional[str] = None
  client_tax_code: Optional[str] = None
  client_country: CountryAlpha2
  bank_account: str
  bank_name: str
  swift: str
  vat_exemption_reason: Optional[None] = None # TODO
  sale_type: InfaktInvoiceEntitySaleType
  invoice_date_kind: InfaktInvoiceEntitySaleDateKind
  document_markings_ids: List[str]
  transaction_kind_id: Optional[int] = None # TODO: Document?
  bdo_code: Optional[None] = None # TODO
  receipt_number: Optional[None] = None # TODO
  not_income: bool
  vat_exchange_date_kind: Optional[InfaktInvoiceEntityVatExchangeDateKind] = None
  sales_kind: InfaktInvoiceEntitySalesKind
  amount_in_words: str
  building_service: bool
  created_at: datetime
  reconciliation_id: Optional[None] = None # TODO
  services: List[InfaktInvoiceService]

class InfaktInvoiceEntity(InfaktInvoiceEntityShared):
  pass

class InfaktInvoiceResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktInvoiceEntity]

class InfaktInvoiceEntityDetails(InfaktInvoiceEntityShared):
  local_government_recipient_address: Optional[str] = None
  local_government_seller_address: Optional[str] = None
  related_documents: List[None] # TODO
  extensions: InfaktInvoiceEntityExtensions
  ksef_data: Optional[InfaktInvoiceEntityKsefData] = None

# Corrective Invoice

class InfaktCorrectiveInvoiceKind(str, Enum):
  CORRECTION = 'correction'

class InfaktCorrectiveInvoiceService(BaseModel, extra='forbid'):
  id: int
  name: str
  tax_symbol: str
  unit: str
  quantity: int
  unit_net_price: int
  net_price: int
  gross_price: int
  tax_price: int
  symbol: str
  pkwiu: Optional[str] = None
  cn: Optional[str] = None
  pkob: Optional[str] = None
  flat_rate_tax_symbol: Optional[str] = None
  discount: str
  unit_net_price_before_discount: int
  gtu_id: Optional[str] = None # TODO: Confirm type
  group: int # TODO?
  related_id: Optional[int] = None # TODO: Confirm type
  correction: bool

class InfaktCorrectiveInvoiceEntityShared(BaseModel, extra='forbid'):
  id: int
  uuid: str
  number: str
  currency: Currency
  paid_price: int
  notes: str
  kind: InfaktCorrectiveInvoiceKind
  payment_method: InfaktInvoiceEntityPaymentMethod
  split_payment: bool
  split_payment_type: Optional[None] = None # TODO
  recipient_signature: str
  seller_signature: str
  invoice_date: ddate
  sale_date: ddate
  vat_date_value: InfaktInvoiceEntityInvoiceDateKind
  continuous_service_start_on: Optional[None] = None # TODO
  continuous_service_end_on: Optional[None] = None # TODO
  occasional_sale: bool
  status: InfaktInvoiceEntityStatus
  payment_date: ddate
  paid_date: Optional[ddate] = None
  net_price: int
  tax_price: int
  gross_price: int
  left_to_pay: int
  client_id: Optional[int] = None
  client_uuid: Optional[str] = None
  client_company_name: Optional[str] = None
  client_first_name: Optional[str] = None
  client_last_name: Optional[str] = None
  client_business_activity_kind: Optional[InfaktInvoiceEntityBusinessActivityKind] = None
  client_street: Optional[str] = None
  client_street_number: Optional[str] = None
  client_flat_number: Optional[str] = None
  client_city: Optional[str] = None
  client_post_code: Optional[str] = None
  client_tax_code: Optional[str] = None
  client_country: CountryAlpha2
  bank_account: str
  bank_name: str
  swift: str
  vat_exemption_reason: Optional[None] = None # TODO
  sale_type: InfaktInvoiceEntitySaleType
  invoice_date_kind: InfaktInvoiceEntitySaleDateKind
  document_markings_ids: List[str]
  transaction_kind_id: Optional[int] = None # TODO: Document?
  bdo_code: Optional[None] = None # TODO
  receipt_number: Optional[None] = None # TODO
  not_income: bool
  vat_exchange_date_kind: Optional[InfaktInvoiceEntityVatExchangeDateKind] = None
  corrected_invoice_number: str
  corrected_invoice_date: ddate
  confirmation: bool
  confirmation_date: ddate
  correction_reason: str
  services: List[InfaktCorrectiveInvoiceService]

class InfaktCorrectiveInvoiceEntity(InfaktCorrectiveInvoiceEntityShared):
  pass

class InfaktCorrectiveInvoiceResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktCorrectiveInvoiceEntity]

class InfaktCorrectiveInvoiceEntityDetails(InfaktCorrectiveInvoiceEntityShared):
  ksef_data: Optional[InfaktInvoiceEntityKsefData] = None