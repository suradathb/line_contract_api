from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PaymentInquiryResponse(BaseModel):
    contract_no: str
    customer_name: str
    installment_no: int
    due_date: date
    due_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: str
    receipt_no: str | None = None


class PaymentHistoryItemResponse(BaseModel):
    contract_no: str
    installment_no: int
    due_date: date
    due_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: str
    payment_date: date | None = None
    receipt_no: str | None = None
