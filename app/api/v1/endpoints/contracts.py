from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.schemas.contracts import ContractResponse, ContractImportRequest, ContractImportResponse
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["ContractMaster"])


@router.get("/by-line/{line_user_id}", response_model=ContractResponse)
async def get_contract_by_line_user_id(
    line_user_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> ContractResponse:
    request_ref = str(uuid4())

    service = ContractService(ContractRepository(db))
    response = await service.get_contract_by_line_user_id(line_user_id)

    await ApiLogRepository(db).create(
        api_name="GetContractByLineUserId",
        request_ref=request_ref,
        response_code="200",
        contract_no=response.contract_no,
        line_user_id=line_user_id,
        api_direction="INBOUND",
        source_system="LINE",
        target_system="API",
        response_payload=str(response.model_dump(mode="json")),
    )
    await db.commit()
    return response


@router.get("/{contract_no}", response_model=ContractResponse)
async def get_contract_by_contract_no(
    contract_no: str,
    db: AsyncSession = Depends(get_db_session),
) -> ContractResponse:
    request_ref = str(uuid4())

    service = ContractService(ContractRepository(db))
    response = await service.get_contract_by_contract_no(contract_no)

    await ApiLogRepository(db).create(
        api_name="GetContractByContractNo",
        request_ref=request_ref,
        response_code="200",
        contract_no=contract_no,
        api_direction="INBOUND",
        source_system="ERP",
        target_system="API",
        response_payload=str(response.model_dump(mode="json")),
    )
    await db.commit()
    return response

@router.post("/import", response_model=ContractImportResponse)
async def import_contracts(
    payload: ContractImportRequest,
    db: AsyncSession = Depends(get_db_session),
):
    service = ContractService(ContractRepository(db))
    response = await service.import_contracts(payload)

    await db.commit()
    return response