from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ContractResponse(BaseModel):
    contract_no: str
    customer_id: str
    id_card_no: str
    customer_name: str
    mobile_no: str
    installment_amount: Decimal
    due_date: date
    contract_status: str

    model_config = {"from_attributes": True}
