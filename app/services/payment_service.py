from fastapi import HTTPException, status

from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payments import PaymentHistoryItemResponse, PaymentInquiryResponse


class PaymentService:
    def __init__(
        self,
        contract_repo: ContractRepository,
        line_mapping_repo: LineMappingRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        self.contract_repo = contract_repo
        self.line_mapping_repo = line_mapping_repo
        self.payment_repo = payment_repo

    async def get_payment_inquiry_by_line_user_id(self, line_user_id: str) -> PaymentInquiryResponse:
        mapping = await self.line_mapping_repo.get_active_by_line_user_id(line_user_id)
        if not mapping:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active LINE mapping not found.")

        contract = await self.contract_repo.get_by_contract_no(mapping.contract_no)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")

        payment = await self.payment_repo.get_latest_inquiry_by_contract_no(contract.contract_no)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment information not found.")

        return PaymentInquiryResponse(
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            installment_no=payment.installment_no,
            due_date=payment.due_date,
            due_amount=payment.due_amount,
            paid_amount=payment.paid_amount,
            outstanding_amount=payment.outstanding_amount,
            payment_status=payment.payment_status,
            receipt_no=payment.receipt_no,
        )

    async def get_payment_history_by_line_user_id(self, line_user_id: str) -> list[PaymentHistoryItemResponse]:
        mapping = await self.line_mapping_repo.get_active_by_line_user_id(line_user_id)
        if not mapping:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active LINE mapping not found.")

        history = await self.payment_repo.get_history_by_contract_no(mapping.contract_no)
        return [PaymentHistoryItemResponse.model_validate(item, from_attributes=True) for item in history]
