from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.customers import CustomerVerifyRequest, CustomerVerifyResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/verify", response_model=CustomerVerifyResponse)
async def verify_customer(payload: CustomerVerifyRequest, db: AsyncSession = Depends(get_db_session)) -> CustomerVerifyResponse:
    service = CustomerService(ContractRepository(db), LineMappingRepository(db))
    response = await service.verify_customer(payload)
    await ApiLogRepository(db).create(
        api_name="VerifyCustomer",
        response_code="200",
        contract_no=payload.contract_no,
        request_payload=payload.model_dump(),
        response_payload=response.model_dump(),
    )
    await db.commit()
    return response
