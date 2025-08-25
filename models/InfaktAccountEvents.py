from pydantic import BaseModel, field_validator
from enum import Enum
from datetime import datetime, date as ddate
from typing import Optional, List

class InfaktAccountEventSubjectDataFormDataAddress(BaseModel, extra='forbid'):
  city: str
  post: str
  street: str
  country: str
  district: str
  province: str
  community: str
  post_code: str
  tax_office: str
  door_number: str
  building_number: str

class InfaktAccountEventSubjectDataFormData(BaseModel, extra='forbid'):
  address: Optional[InfaktAccountEventSubjectDataFormDataAddress] = None
  start_on: Optional[List[str]] = None
  value_id: Optional[str] = None

class InfaktAccountEventSubjectData(BaseModel, extra='forbid'):
  email: Optional[str] = None
  ip_address: Optional[str] = None
  numer: Optional[str] = None
  name: Optional[str] = None
  file_name: Optional[str] = None
  date: Optional[ddate] = None
  month: Optional[str] = None
  bank_name: Optional[str] = None
  explanation: Optional[str] = None
  period: Optional[None] = None
  form_data: Optional[InfaktAccountEventSubjectDataFormData] = None
  client_nip: Optional[str] = None

class InfaktAccountEventActionSymbol(str, Enum):
  LOGIN = 'login'
  ADD_FILE = 'add_file'
  ADD_ATTACHMENT = 'add_attachment'
  REMOVE_ATTACHMENT = 'remove_attachment' # Usunięcie załącznika
  ASSIGN_NAMED_DOCUMENT_SCANS = 'assign_named_document_scans' # Dołączenie skanu dokumentu
  ADD_DOCUMENT = 'add_document' # Dodanie do sekcji dokumenty
  IFE_SUBMISSION = 'ife_submission' # Oznaczenie deklaracji ZUS jako wysłany
  IFE_PREVIEW = 'ife_preview' # Podgląd deklaracji ZUS DRA
  IFE_XML = 'ife_xml' # Pobranie deklaracji ZUS
  IFE_FILE_RESET_STATUS = 'ife_file_reset_status' # Zresetowanie statusu składki ZUS
  DESTROY_IFE_CORRECTION = 'destroy_ife_correction' # Usunięcie korekty ZUS
  RECEIVE_UPO = 'receive_upo' # Odebranie UPO
  DECLARATION_SUBMISSION = 'declaration_submission' # Oznaczenie deklaracji PIT jako wysłana
  DOWNLOAD_FILLUP_XML = 'download_fillup_xml' # Pobranie danych do deklaracji Fillup w formacie XML
  PAID = 'paid' # Oznaczenie dokumentu jako zapłacony
  UNPAID = 'unpaid' # Oznaczenie dokumentu jako niezapłacony
  UNPAID_DOCUMENT = 'unpaid_document' # Oznaczenie dokumentu jako niezapłacony
  CREATE = 'create' # Stworzenie dokumentu
  UPDATE = 'update' # Edytowanie dokumentu
  DISCARD = 'discard' # Odrzucenie dokumentu
  DESTROY = 'destroy' # Usunięcie pliku
  PRINT = 'print' # Wydrukowanie dokumentu
  SENT = 'sent' # Oznaczenie dokumentu jako wysłany
  ENVELOPE = 'envelope' # Wydrukowanie koperty dla dokumentu
  PDF = 'pdf' # Wydrukowanie dokumentu
  CREATE_NOTE = 'create_note' # Utworzenie notatki
  ESAF_XML = 'esaf_xml' # Pobranie JPK
  ESAF_SUBMISSION = 'esaf_submission' # Oznaczenie JPK jako wysłany
  UNLOCK_SAF_SUBMISSION = 'unlock_saf_submission' # Odblokowanie możliwości ponownej wysyłki JPK
  PAID_WITH_BLUE_MEDIA = 'paid_with_blue_media' # Zapłacenie za pomocą szybkich płatności
  AUTO_PAID_WITH_BLUE_MEDIA = 'auto_paid_with_blue_media' # Automatycznie zapłacono za pomocą szybkich płatności
  APPROVE_SAF = 'approve_saf' # Zatwierdzenie JPK
  RESET_SCAN_STATUS = 'reset_scan_status' # Zresetowanie statusu
  RESET_COST_STATUS = 'reset_cost_status' # Zresetowanie statusu dokumentu
  SEND_SIGNED_DOCUMENT = 'send_signed_document' # Wysłanie dokumentu do urzędu za pomcoą podpisu kwalifikowanego
  AUTOMATIC_SUSPENSION_ON_START = 'automatic_suspension_on_start' # Nowy okres zawieszenia działalności
  MONTH_COMPLETED = 'month_completed' # Zaksięgowano miesiąc
  SAF_V7_REFUNDS = 'saf_v7_refunds' # Zgłoszenie zwrotu podatku
  SAF_V7_RESET_STATUS = 'saf_v7_reset_status' # Zresetowanie statusu JPK
  SAF_V7_DESTROY_CORRECTION_WITHOUT_RESET = 'saf_v7_destroy_correction_without_reset' # Usunięcie rozliczenia korekty bez przeliczenia JPK
  SAF_V7_DESTROY_CORRECTION = 'saf_v7_destroy_correction' # Usunięcie rozliczenia korekty JPK
  ADD_HOLIDAYS = 'add_holidays' # Dodanie Wakacji od ZUS
  MOVE_SCAN_TO_MONTH = 'move_scan_to_month' # Przeniesienie do innego okresu
  MOVE_SCAN_TO_DOCUMENTS = 'move_scan_to_documents' # Przeniesienie do dokumentów
  ASSIGN_COST_CATEGORY = 'assign_cost_category' # Przypisanie kategorii kosztu
  CREATE_CLIENT = 'create_client' # Stworzenie klienta
  UPDATE_CLIENT = 'update_client' # Edycja klienta
  CREATE_PRODUCT = 'create_product' # Stworzenie produktu
  APPROVE_DECLARATION = 'approve_declaration' # Zatwierdzenie deklaracji
  PAID_DECLARATION = 'paid_declaration' # Oznaczenie deklaracji jako zapłacona
  PRINT_DECLARATION = 'print_declaration' # Wydrukowanie deklaracji
  PRINT_DECLARATION_PREVIEW = 'print_declaration_preview' # Wydrukowanie podglądu deklaracji
  DISCARD_DECLARATION = 'discard_declaration' # Wycofanie złożonej deklaracji
  BANKING_CREATE_INTEGRATION = 'banking_create_integration' # Połączenie rachunku
  BANKING_AUTO_DESTROY_INTEGRATION = 'banking_auto_destroy_integration' # Automatyczne rozłączenie rachunku
  BANKING_EXPIRE_INTEGRATION = 'banking_expire_integration' # Wygaśnięcie integracji z rachunkiem
  BANKING_REFRESH_INTEGRATION = 'banking_refresh_integration' # Odświeżenie integracji z rachunkiem
  BANKING_DESTROY_INTEGRATION = 'banking_destroy_integration' # Rozłączenie rachunku
  USER_PASSWORD_CHANGED = 'user_password_changed' # Zmiana hasła do aplikacji
  LIQUIDATION = 'liquidation' # Zlikwidowanie
  MARK_ACCOUNTABLE = 'mark_accountable' # Uwzględnienie raportu w księgowości i oznaczenie jako opłacony
  DEACTIVATE = 'deactivate' # Ustawienie jako nieaktywny
  ACTIVATE = 'activate' # Ustawienie jako aktywny
  CHANGE_COMPANY_ADDRESS_SECTION = 'settings/company_address_section' # Zmiana adresu prowadzenia działalności
  CHANGE_PIT_TYPE = 'settings/pit_type' # Zmiana sposobu rozliczania podatku dochodowego

class InfaktAccountEventDevice(str, Enum):
  WWW_APPLICATION = 'Aplikacja www'
  ANDROID = 'Android'
  NONE = ''

class InfaktAccountEventBlameRole(str, Enum):
  OWNER = 'owner'
  ACCOUNTANT = 'accountant'

class InfaktAccountEventBlame(BaseModel, extra='forbid'):
  uuid: Optional[str] = None
  email: Optional[str] = None
  fullname: Optional[str] = None
  role: Optional[InfaktAccountEventBlameRole] = None

class InfaktAccountEvent(BaseModel, extra='forbid'):
  id: int
  user: str
  subject_id: int
  subject_type: str
  subject_data: InfaktAccountEventSubjectData
  action_symbol: InfaktAccountEventActionSymbol
  action_name: str
  performed_at: datetime
  device: InfaktAccountEventDevice
  blame: InfaktAccountEventBlame

  @field_validator('performed_at', mode='before')
  @classmethod
  def parse_custom_performed_at(cls, value):
    if isinstance(value, datetime): return value
    return datetime.strptime(value, '%Y-%m-%d, %H:%M:%S')

class InfaktAccountEventsResponse(BaseModel, extra='forbid'):
  total_count: int
  count: int
  entities: List[InfaktAccountEvent]

InfaktAccountEventsIgnoreFields = {}