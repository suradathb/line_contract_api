from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payments import PaymentHistoryItemResponse, PaymentInquiryResponse
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/inquiry/by-line/{line_user_id}", response_model=PaymentInquiryResponse)
async def get_payment_inquiry_by_line_user_id(
    line_user_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> PaymentInquiryResponse:
    request_ref = str(uuid4())

    service = PaymentService(
        ContractRepository(db),
        LineMappingRepository(db),
        PaymentRepository(db),
    )
    response = await service.get_payment_inquiry_by_line_user_id(line_user_id)

    await ApiLogRepository(db).create(
        api_name="GetPaymentInquiryByLineUserId",
        request_ref=request_ref,
        response_code="200",
        contract_no=response.contract_no,
        line_user_id=line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.get("/history/by-line/{line_user_id}", response_model=list[PaymentHistoryItemResponse])
async def get_payment_history_by_line_user_id(
    line_user_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> list[PaymentHistoryItemResponse]:
    request_ref = str(uuid4())

    service = PaymentService(
        ContractRepository(db),
        LineMappingRepository(db),
        PaymentRepository(db),
    )
    response = await service.get_payment_history_by_line_user_id(line_user_id)

    await ApiLogRepository(db).create(
        api_name="GetPaymentHistoryByLineUserId",
        request_ref=request_ref,
        response_code="200",
        contract_no=response[0].contract_no if response else None,
        line_user_id=line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        response_payload=[item.model_dump(mode="json") for item in response],
    )
    await db.commit()
    return response