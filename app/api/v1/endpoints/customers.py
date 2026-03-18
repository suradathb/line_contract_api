from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.schemas.customers import (
    CustomerMapRequest,
    CustomerMapResponse,
    CustomerUnmapRequest,
    CustomerUnmapResponse,
    CustomerVerifyRequest,
    CustomerVerifyResponse,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/verify", response_model=CustomerVerifyResponse)
async def verify_customer(
    payload: CustomerVerifyRequest,
    db: AsyncSession = Depends(get_db_session),
) -> CustomerVerifyResponse:
    request_ref = str(uuid4())

    service = CustomerService(ContractRepository(db))
    response = await service.verify_customer(payload)

    await ApiLogRepository(db).create(
        api_name="VerifyCustomer",
        request_ref=request_ref,
        response_code="200",
        contract_no=payload.contract_no,
        line_user_id=payload.line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        request_payload=str(payload.model_dump(mode="json")),
        response_payload=str(response.model_dump(mode="json")),
    )
    await db.commit()
    return response


@router.post("/map", response_model=CustomerMapResponse)
async def map_customer(
    payload: CustomerMapRequest,
    db: AsyncSession = Depends(get_db_session),
) -> CustomerMapResponse:
    request_ref = str(uuid4())

    service = CustomerService(ContractRepository(db))

    try:
        response = await service.map_customer(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    await ApiLogRepository(db).create(
        api_name="MapCustomer",
        request_ref=request_ref,
        response_code="200",
        contract_no=payload.contract_no,
        line_user_id=payload.line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        request_payload=str(payload.model_dump(mode="json")),
        response_payload=str(response.model_dump(mode="json")),
    )
    await db.commit()
    return response


@router.post("/unmap", response_model=CustomerUnmapResponse)
async def unmap_customer(
    payload: CustomerUnmapRequest,
    db: AsyncSession = Depends(get_db_session),
) -> CustomerUnmapResponse:
    request_ref = str(uuid4())

    service = CustomerService(ContractRepository(db))

    try:
        response = await service.unmap_customer(payload.contract_no)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    await ApiLogRepository(db).create(
        api_name="UnmapCustomer",
        request_ref=request_ref,
        response_code="200",
        contract_no=payload.contract_no,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        request_payload=str(payload.model_dump(mode="json")),
        response_payload=str(response.model_dump(mode="json")),
    )
    await db.commit()
    return response