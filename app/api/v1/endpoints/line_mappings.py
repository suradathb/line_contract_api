from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.line_mappings import (
    LineMappingCreateRequest,
    LineMappingResponse,
    LineUnmapRequest,
    LineUnmapResponse,
)
from app.services.line_mapping_service import LineMappingService

router = APIRouter(prefix="/line-mappings", tags=["LINE Mappings"])


@router.post("", response_model=LineMappingResponse)
async def create_line_mapping(
    payload: LineMappingCreateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> LineMappingResponse:
    request_ref = str(uuid4())

    service = LineMappingService(
        ContractRepository(db),
        LineMappingRepository(db),
    )
    response = await service.map_line_user(payload)

    await ApiLogRepository(db).create(
        api_name="MapLineUser",
        request_ref=request_ref,
        response_code="200",
        contract_no=payload.contract_no,
        line_user_id=payload.line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        request_payload=payload.model_dump(mode="json"),
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response


@router.post("/unmap", response_model=LineUnmapResponse)
async def unmap_line_mapping(
    payload: LineUnmapRequest,
    db: AsyncSession = Depends(get_db_session),
) -> LineUnmapResponse:
    request_ref = str(uuid4())

    service = LineMappingService(
        ContractRepository(db),
        LineMappingRepository(db),
    )
    response = await service.unmap_line_user(payload)

    await ApiLogRepository(db).create(
        api_name="UnmapLineUser",
        request_ref=request_ref,
        response_code="200",
        contract_no=response.contract_no,
        line_user_id=payload.line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        request_payload=payload.model_dump(mode="json"),
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response