from decimal import Decimal

from pydantic import BaseModel


class ContractResponse(BaseModel):
    contract_no: str
    customer_name: str
    contract_status: str
    total_outstanding_amount: Decimal
    line_user_id: str | None = None
    line_display_name: str | None = None
    line_map_status: str

class ContractImportItem(BaseModel):
    contract_no: str
    customer_name: str
    contract_status: str
    total_outstanding_amount: Decimal


class ContractImportRequest(BaseModel):
    contracts: list[ContractImportItem]


class ContractImportResponse(BaseModel):
    success: bool
    inserted: int
    updated: int
    total: int

class ContractImportCsvResult(BaseModel):
    success: bool
    inserted: int
    updated: int
    failed: int
    total: int
    message: str
    errors: list[str] = []