from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payments import (
    MarkPaymentSentResponse,
    NextPaymentToSendResponse,
    PaymentHistoryItemResponse,
    PaymentImportResult,
    PaymentInquiryResponse,
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/inquiry/by-line/{line_user_id}", response_model=PaymentInquiryResponse)
async def get_payment_inquiry_by_line_user_id(
    line_user_id: str,
    billing_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db_session),
) -> PaymentInquiryResponse:
    request_ref = str(uuid4())

    service = PaymentService(
        ContractRepository(db),
        PaymentRepository(db),
    )
    response = await service.get_payment_inquiry_by_line_user_id(line_user_id, billing_date)

    await ApiLogRepository(db).create(
        api_name="GetPaymentInquiryByLineUserId",
        request_ref=request_ref,
        response_code="200",
        contract_no=response.contract_no,
        line_user_id=line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        request_payload={
            "billing_date": billing_date.isoformat(),
        },
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


@router.post("/import-csv", response_model=PaymentImportResult)
async def import_payments_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
) -> PaymentImportResult:
    request_ref = str(uuid4())

    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()

    service = PaymentService(
        ContractRepository(db),
        PaymentRepository(db),
    )
    response = await service.import_payment_schedules_csv(content)

    await ApiLogRepository(db).create(
        api_name="ImportPaymentSchedulesCsv",
        request_ref=request_ref,
        response_code="200",
        api_direction="INBOUND",
        source_system="TAXI",
        target_system="API",
        request_payload={
            "filename": file.filename,
            "content_type": file.content_type,
        },
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.get("/export-csv")
async def export_payments_csv(
    contract_no: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    request_ref = str(uuid4())

    service = PaymentService(
        ContractRepository(db),
        PaymentRepository(db),
    )
    csv_content = await service.export_payment_schedules_csv(contract_no=contract_no)

    await ApiLogRepository(db).create(
        api_name="ExportPaymentSchedulesCsv",
        request_ref=request_ref,
        response_code="200",
        contract_no=contract_no,
        api_direction="OUTBOUND",
        source_system="API",
        target_system="CLIENT",
        request_payload={"contract_no": contract_no} if contract_no else None,
        response_payload={
            "filename": "payment_schedules_export.csv",
            "contract_no": contract_no,
        },
    )
    await db.commit()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=payment_schedules_export.csv"},
    )


@router.get("/{contract_no}/next-to-send", response_model=NextPaymentToSendResponse)
async def get_next_payment_to_send(
    contract_no: str,
    db: AsyncSession = Depends(get_db_session),
) -> NextPaymentToSendResponse:
    request_ref = str(uuid4())

    service = PaymentService(
        ContractRepository(db),
        PaymentRepository(db),
    )
    response = await service.get_next_payment_to_send(contract_no)

    await ApiLogRepository(db).create(
        api_name="GetNextPaymentToSend",
        request_ref=request_ref,
        response_code="200",
        contract_no=contract_no,
        line_user_id=response.line_user_id,
        api_direction="INBOUND",
        source_system="API",
        target_system="API",
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post("/{payment_id}/mark-sent", response_model=MarkPaymentSentResponse)
async def mark_payment_sent(
    payment_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> MarkPaymentSentResponse:
    request_ref = str(uuid4())

    service = PaymentService(
        ContractRepository(db),
        PaymentRepository(db),
    )

    try:
        response = await service.mark_payment_sent(payment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    await ApiLogRepository(db).create(
        api_name="MarkPaymentSent",
        request_ref=request_ref,
        response_code="200",
        contract_no=response.contract_no,
        api_direction="INBOUND",
        source_system="API",
        target_system="API",
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response