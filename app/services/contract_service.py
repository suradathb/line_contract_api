from fastapi import HTTPException, status

from app.repositories.contract_repository import ContractRepository
from app.schemas.contracts import ContractResponse, ContractImportRequest, ContractImportResponse


class ContractService:
    def __init__(self, contract_repo: ContractRepository) -> None:
        self.contract_repo = contract_repo

    async def get_contract_by_line_user_id(self, line_user_id: str) -> ContractResponse:
        contract = await self.contract_repo.get_by_line_user_id(line_user_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found for this LINE user.",
            )

        return ContractResponse(
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            contract_status=contract.contract_status,
            total_outstanding_amount=contract.total_outstanding_amount,
            line_user_id=contract.line_user_id,
            line_display_name=contract.line_display_name,
            line_map_status=contract.line_map_status,
        )

    async def get_contract_by_contract_no(self, contract_no: str) -> ContractResponse:
        contract = await self.contract_repo.get_by_contract_no(contract_no)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found.",
            )

        return ContractResponse(
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            contract_status=contract.contract_status,
            total_outstanding_amount=contract.total_outstanding_amount,
            line_user_id=contract.line_user_id,
            line_display_name=contract.line_display_name,
            line_map_status=contract.line_map_status,
        )
    
    async def import_contracts(self, payload: ContractImportRequest):
        inserted = 0
        updated = 0

        for item in payload.contracts:
            result = await self.repo.upsert_contract(
                contract_no=item.contract_no,
                customer_name=item.customer_name,
                contract_status=item.contract_status,
                total_outstanding_amount=item.total_outstanding_amount,
            )

            if result == "inserted":
                inserted += 1
            else:
                updated += 1

        return ContractImportResponse(
            success=True,
            inserted=inserted,
            updated=updated,
            total=len(payload.contracts),
        )