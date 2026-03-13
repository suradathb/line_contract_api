from fastapi import HTTPException, status

from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.contracts import ContractResponse


class ContractService:
    def __init__(self, contract_repo: ContractRepository, line_mapping_repo: LineMappingRepository) -> None:
        self.contract_repo = contract_repo
        self.line_mapping_repo = line_mapping_repo

    async def get_contract_by_line_user_id(self, line_user_id: str) -> ContractResponse:
        mapping = await self.line_mapping_repo.get_active_by_line_user_id(line_user_id)
        if not mapping:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active LINE mapping not found.")
        contract = await self.contract_repo.get_by_contract_no(mapping.contract_no)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")
        return ContractResponse.model_validate(contract)
