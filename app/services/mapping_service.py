from datetime import datetime

from app.repositories.contract_repository import ContractRepository


class MappingService:
    def __init__(self, contract_repo: ContractRepository) -> None:
        self.contract_repo = contract_repo

    async def map_line_user(
        self,
        contract_no: str,
        line_user_id: str,
        line_display_name: str | None = None,
    ):
        contract = await self.contract_repo.get_by_contract_no(contract_no)
        if not contract:
            raise ValueError("Contract not found.")

        if contract.line_user_id:
            raise ValueError("Contract is already mapped.")

        existing_line = await self.contract_repo.get_by_line_user_id(line_user_id)
        if existing_line:
            raise ValueError("LINE user is already mapped to another contract.")

        contract.line_user_id = line_user_id
        contract.line_display_name = line_display_name
        contract.line_map_status = "ACTIVE"
        contract.line_mapped_at = datetime.utcnow()

        return await self.contract_repo.save(contract)

    async def unmap_line_user(self, contract_no: str):
        contract = await self.contract_repo.get_by_contract_no(contract_no)
        if not contract:
            raise ValueError("Contract not found.")

        contract.line_user_id = None
        contract.line_display_name = None
        contract.line_map_status = "UNMAPPED"
        contract.line_mapped_at = None

        return await self.contract_repo.save(contract)