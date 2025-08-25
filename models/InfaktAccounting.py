from pydantic import BaseModel
from typing import List, Optional
from datetime import date as ddate, datetime
from enum import Enum

from models.InfaktPaginateResponseMetainfo import InfaktPaginateResponseMetainfo

class InfaktAccountingEntityStatus(str, Enum):
  DRAFT = 'draft'
  PAID = 'paid'
  UNPAID = 'unpaid'
  SENT = 'sent'
  PRINTED = 'printed'
  NOT_APPLICABLE = 'not_applicable'

class InfaktPeriodType(str, Enum):
  MONTH = 'M'

class InfaktAccountingEntityTaxOffice(BaseModel, extra='forbid'):
  info: str
  name: str
  bank_name: str
  account_number: str

class InfaktAccountingEntityExtentionPayments(BaseModel, extra='forbid'):
  enabled: bool
  pragma_offer_details_link: Optional[str] = None

class InfaktAccountingEntityExtentions(BaseModel, extra='forbid'):
  payments: InfaktAccountingEntityExtentionPayments

# SAF V7

class InfaktSAFV7Symbol(str, Enum):
  JPK_V7M = 'JPK-V7M'

class InfaktSAFV7EntityShared(BaseModel, extra='forbid'):
  id: int
  uuid: str
  symbol: InfaktSAFV7Symbol
  period: ddate
  period_name: str
  correction_counter: int
  payment_date: ddate
  tax_to_pay_price: int
  real_pay: int
  status: InfaktAccountingEntityStatus

class InfaktSAFV7Entity(InfaktSAFV7EntityShared):
  automatically_paid: bool
  automatically_paid_on: Optional[datetime] = None

class InfaktSAFV7Response(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktSAFV7Entity]

class InfaktSAFV7EntityDetails(InfaktSAFV7EntityShared):
  tax_office: InfaktAccountingEntityTaxOffice
  extensions: InfaktAccountingEntityExtentions

# VAT EU

class InfaktVATEUSymbol(str, Enum):
  VAT_UE = 'VAT-UE'

class InfaktVATEUEntityShared(BaseModel, extra='forbid'):
  id: int
  symbol: InfaktVATEUSymbol
  period: ddate
  period_name: str
  period_type: InfaktPeriodType
  correction_counter: int
  payment_date: ddate
  services_price: int
  sell_cargo_price: int
  purchase_cargo_price: int
  status: InfaktAccountingEntityStatus

class InfaktVATEUEntity(InfaktVATEUEntityShared):
  pass

class InfaktVATEUResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktVATEUEntity]

class InfaktVATEUEntityDetails(InfaktVATEUEntityShared):
  pass

# Income Tax

class InfaktIncomeTaxSymbol(str, Enum):
  PIT_5 = 'PIT-5'
  PPE = 'PPE'

class InfaktIncomeTaxEntityShared(BaseModel, extra='forbid'):
  id: int
  uuid: str
  symbol: str
  period: ddate
  period_name: str
  period_type: InfaktPeriodType
  correction_counter: int
  payment_date: ddate
  incremental_income_price: Optional[int] = None
  incremental_cost_price: Optional[int] = None
  period_proceeds_price: Optional[int] = None
  incremental_proceeds_price: Optional[int] = None
  to_pay_price: int
  status: InfaktAccountingEntityStatus
  real_pay: int

class InfaktIncomeTaxEntity(InfaktIncomeTaxEntityShared):
  automatically_paid: bool
  automatically_paid_on: Optional[datetime] = None

class InfaktIncomeTaxResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktIncomeTaxEntity]

class InfaktIncomeTaxEntityDetails(InfaktIncomeTaxEntityShared):
  period_income_price: int
  period_cost_price: Optional[int] = None
  incremental_social_insurance_price: int
  incremental_health_insurance_price: int
  tax_paid_in_year_price: Optional[int] = None
  tax_office: InfaktAccountingEntityTaxOffice
  extensions: InfaktAccountingEntityExtentions

# Book (KPiR)

class InfaktBookEntityShared(BaseModel, extra='forbid'):
  id: int
  period: ddate
  period_name: str

class InfaktBookEntity(InfaktBookEntityShared):
  income_price: int
  expenses_price: int
  profit_price: int
  status: InfaktAccountingEntityStatus

class InfaktBookResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktBookEntity]

class InfaktBookCompany(BaseModel, extra='forbid'):
  name: str
  taxid: str
  full_address: str

class InfaktBookTransfered(BaseModel, extra='forbid'):
  income_cargo_services: int
  income_others: int
  income_summary: int
  expense_cargo_material: int
  expense_incidental: int
  expense_salary: int
  expense_others: int
  expense_sum: int
  expense_research: int

class InfaktBookLine(InfaktBookTransfered):
  # Below fields are none for "spis z natury"
  ordinal: Optional[int] = None
  date: Optional[ddate] = None
  number: Optional[str] = None
  client_name: Optional[str] = None
  client_address: Optional[str] = None
  description: str

class InfaktBookEntityDetails(InfaktBookEntityShared):
  date: ddate
  company: InfaktBookCompany
  transfered: InfaktBookTransfered
  lines: List[InfaktBookLine]

# Insurance

class InfaktInsuranceEntityShared(BaseModel, extra='forbid'):
  id: int
  uuid: str
  period: ddate
  period_name: str
  correction: bool
  correction_counter: int
  payment_date: ddate
  social_amount_price: int
  health_amount_price: int
  work_amount_price: int
  social_amount_paid: int
  health_amount_paid: int
  work_amount_paid: int
  sum_amount_price: int
  real_pay: int
  show_payment_option: bool
  status: InfaktAccountingEntityStatus
  annual_settlement_amount_price: int
  annual_settlement_amount_paid: int
  show_annual_settlement: bool
  automatically_paid: bool
  automatically_paid_on: Optional[datetime] = None

class InfaktInsuranceEntity(InfaktInsuranceEntityShared):
  pass

class InfaktInsuranceResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktInsuranceEntity]

class InfaktInsuranceEntityDetails(InfaktInsuranceEntityShared):
  social_account_number: str
  health_account_number: str
  work_account_number: str
  extensions: InfaktAccountingEntityExtentions