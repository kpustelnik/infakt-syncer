from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

from models.InfaktPaginateResponseMetainfo import InfaktPaginateResponseMetainfo

class InfaktAccountingEntityStatus(str, Enum):
  DRAFT = 'draft'
  PAID = 'paid'
  PRINTED = 'printed'

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
  period: date
  period_name: str
  correction_counter: int
  payment_date: date
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
  extentions: InfaktAccountingEntityExtentions

# VAT EU

class InfaktVATEUSymbol(str, Enum):
  VAT_UE = 'VAT-UE'

class InfaktVATEUEntityShared(BaseModel, extra='forbid'):
  id: int
  symbol: InfaktVATEUSymbol
  period: date
  period_name: str
  period_type: InfaktPeriodType
  correction_counter: int
  payment_date: date
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
  period: date
  period_name: str
  period_type: InfaktPeriodType
  correction_counter: int
  payment_date: date
  to_pay_price: int
  status: InfaktAccountingEntityStatus
  real_pay: int

class InfaktIncomeTaxEntity(InfaktIncomeTaxEntityShared):
  # incremental_income_price: int
  # incremental_cost_price: int
  # incremental_proceeds_price: int
  # period_proceeds_price: int
  automatically_paid: bool
  automatically_paid_on: Optional[datetime] = None

class InfaktIncomeTaxResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktIncomeTaxEntity]

class InfaktIncomeTaxEntityDetails(InfaktIncomeTaxEntityShared):
  period_income_price: int
  incremental_social_insurance_price: int
  incremental_health_insurance_price: int
  tax_office: InfaktAccountingEntityTaxOffice
  extentions: InfaktAccountingEntityExtentions

# Book (KPiR)

class InfaktBookEntityShared(BaseModel, extra='forbid'):
  id: int
  period: date
  period_name: str
  income_price: int
  expenses_price: int
  profit_price: int
  status: InfaktAccountingEntityStatus

class InfaktBookEntity(InfaktBookEntityShared):
  pass

class InfaktBookResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktBookEntity]

class InfaktBookCompany(BaseModel, extra='forbid'):
  name: str
  taxid: str
  full_address: str

class InfaktBookEntityDetails(InfaktBookEntityShared):
  date: date
  company: InfaktBookCompany
  pass # TODO: Confirm if error is thrown!

# Insurance

class InfaktInsuranceEntityShared(BaseModel, extra='forbid'):
  id: int
  period_name: str
  payment_date: date
  social_amount_price: int
  health_amount_price: int
  work_amount_price: int
  social_amount_paid: int
  health_amount_paid: int
  work_amount_paid: int
  sum_amount_price: int
  show_payment_option: bool
  status: InfaktAccountingEntityStatus

class InfaktInsuranceEntity(InfaktInsuranceEntityShared):
  pass

class InfaktInsuranceResponse(BaseModel, extra='forbid'):
  metainfo: InfaktPaginateResponseMetainfo
  entities: List[InfaktInsuranceEntity]

class InfaktInsuranceEntityDetails(InfaktInsuranceEntityShared):
  pass