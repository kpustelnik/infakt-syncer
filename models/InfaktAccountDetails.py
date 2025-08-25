from pydantic import BaseModel, field_validator
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

class InfaktAccountDataRole(str, Enum):
  OWNER = 'owner'
  COLLABORATOR = 'collaborator'
  EMPLOYEE = 'employee'
  INVOICER = 'invoicer'

class InfaktAccountData(BaseModel, extra='forbid'):
  uuid: str
  email: str
  username: str
  site: str
  role: InfaktAccountDataRole
  registered_at: datetime

  @field_validator('registered_at', mode='before')
  @classmethod
  def parse_custom_registered_at(cls, value):
    if isinstance(value, datetime): return value
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S %z')

class InfaktCompanyData(BaseModel, extra='forbid'):
  first_name: str
  last_name: str
  company_name: str
  owner_name: str
  owner_surname: str
  street: str
  street_name: str
  street_number: str
  flat_number: str
  city: str
  postal_code: str
  tax_id: str
  pesel: str
  regon: str
  phone_number: str
  mailing_company_name: Optional[str] = None
  mailing_street: Optional[str] = None
  mailing_city: Optional[str] = None
  mailing_postal_code: Optional[str] = None
  business_activity_code: str

class InfaktSubscriptionDataType(str, Enum):
  FREE = 'free'
  PDK = 'pdk'
  OBR_SELF_EMPLOYED_FOUNDATION = 'obr_self_employed_foundation'
  OBR_SELF_EMPLOYED = 'obr_self_employed'
  OBR_COPARTNERSHIP = 'obr_copartnership'
  OBR_COPARTNERSHIP_FOUNDATION = 'obr_copartnership_foundation'
  UNKNOWN = 'unknown'
  TRIAL = 'trial'
  BASIC_PACKAGE = 'basic_package'
  OPTIMUM_PACKAGE = 'optimum_package'
  PREMIUM_PACKAGE = 'premium_package'

class InfaktSubscriptionData(BaseModel, extra='forbid'):
  name: str
  expired_on: date
  days_until_expiration: int
  user_type_symbol: InfaktSubscriptionDataType
  recurring_payment: bool

class InfaktAccountingSettingsStatus(str, Enum):
  FINISHED = 'finished'

class InfaktAccountingPitTypeValue(str, Enum):
  FLAT_RATE = 'flat_rate'
  REGULAR = 'regular'

class InfaktAccountingPitType(BaseModel, extra='forbid'):
  value: InfaktAccountingPitTypeValue
  label: str

class InfaktAccountingPitTypeHistory(InfaktAccountingPitType):
  start_on: datetime
  finish_on: Optional[datetime] = None

class InfaktAccountingVatSalesValue(str, Enum):
  TAXED = 'taxed'

class InfaktAccountingVatSales(BaseModel, extra='forbid'):
  value: InfaktAccountingVatSalesValue
  label: str
  ratio: int

class InfaktAccountingVatMethodValue(str, Enum):
  MEMORIAL = 'memorial'

class InfaktAccountingVatMethod(BaseModel, extra='forbid'):
  value: InfaktAccountingVatMethodValue
  label: str

class InfaktAccountingZusValue(str, Enum):
  STANDARD = 'standard_zus'
  CUTTED = 'cutted_zus' # ZUS obniżony

class InfaktAccountingZus(BaseModel, extra='forbid'):
  value: InfaktAccountingZusValue
  label: str

class InfaktAccountingSettings(BaseModel, extra='forbid'):
  status: InfaktAccountingSettingsStatus
  accounting_data_filled: bool
  pit_type: InfaktAccountingPitType
  pit_history: List[InfaktAccountingPitTypeHistory]
  vat_sales: InfaktAccountingVatSales
  vat_method: InfaktAccountingVatMethod
  started_at_in_infakt: date
  business_activity_code: str
  insurance_fee_account_number: Optional[str] = None
  individual_tax_account_number: Optional[str] = None
  zus: InfaktAccountingZus

class InfaktAccountingOfficeService(BaseModel, extra='forbid'):
  active: bool
  last_accounted_month: Optional[date] = None
  service_global_name: str

class InfaktFoundationProcessObrType(str, Enum):
  SELF_EMPLOYED_FOUNDATION = 'self_employed_foundation'

class InfaktFoundationProcessStatus(str, Enum):
  DONE = 'done'

class InfaktFoundationProcess(BaseModel, extra='forbid'):
  in_progress: bool
  completed: bool
  obr_type: InfaktFoundationProcessObrType
  current_step: InfaktFoundationProcessStatus
  with_bank_account: bool
  show_company_status_details: bool

class InfaktAmlProcessStatus(str, Enum):
  COMPLETED = 'completed'

class InfaktAmlProcess(BaseModel, extra='forbid'):
  status: InfaktAmlProcessStatus
  in_progress: bool
  completed: bool

class InfaktExtensionAmbassadorDetails(BaseModel, extra='forbid'):
  link: str
  pending_withdraw: int

class InfaktExtensionAmbassador(BaseModel, extra='forbid'):
  name: str
  active: bool
  details: InfaktExtensionAmbassadorDetails

class InfaktExtensionKsef(BaseModel, extra='forbid'):
  name: str
  active: bool

class InfaktExtensionMerit(BaseModel, extra='forbid'):
  name: str
  active: bool

class InfaktExtensionAutopay(BaseModel, extra='forbid'):
  name: str
  max_single_transaction_limit_in_cents: int
  integration_confirmed: bool

class InfaktExtensions(BaseModel, extra='forbid'):
  ambassador: InfaktExtensionAmbassador
  ksef: InfaktExtensionKsef
  merit: InfaktExtensionMerit
  autopay: InfaktExtensionAutopay

class InfaktAccountDetails(BaseModel, extra='forbid'):
  account_data: InfaktAccountData
  company_data: InfaktCompanyData
  current_subscription: InfaktSubscriptionData
  accounting_settings: InfaktAccountingSettings
  accounting_office_service: InfaktAccountingOfficeService
  foundation_process: InfaktFoundationProcess
  aml_process: InfaktAmlProcess
  extentions: InfaktExtensions

InfaktAccountDetailsIgnoreFields = {
  'current_subscription': {'days_until_expiration'}
}