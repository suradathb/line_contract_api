from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.contracts import ContractResponse
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get("/by-line/{line_user_id}", response_model=ContractResponse)
async def get_contract_by_line_user_id(line_user_id: str, db: AsyncSession = Depends(get_db_session)) -> ContractResponse:
    service = ContractService(ContractRepository(db), LineMappingRepository(db))
    response = await service.get_contract_by_line_user_id(line_user_id)
    await ApiLogRepository(db).create(
        api_name="GetContractByLineUserId",
        response_code="200",
        contract_no=response.contract_no,
        line_user_id=line_user_id,
        response_payload=response.model_dump(mode="json"),
    )
    await db.commit()
    return response
