from uuid import uuid4

from fastapi import APIRouter, Depends,File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.api_log_repository import ApiLogRepository
from app.repositories.contract_repository import ContractRepository
from app.schemas.contracts import ContractResponse, ContractImportRequest, ContractImportResponse, ContractImportCsvResult
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


@router.post("/import-csv", response_model=ContractImportCsvResult)
async def import_contracts_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
) -> ContractImportCsvResult:
    request_ref = str(uuid4())

    if not file.filename:
        raise HTTPException(status_code=400, detail="File is required.")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()

    service = ContractService(ContractRepository(db))
    response = await service.import_contracts_csv(content)

    await ApiLogRepository(db).create(
        api_name="ImportContractMasterCsv",
        request_ref=request_ref,
        response_code="200" if response.success else "400",
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