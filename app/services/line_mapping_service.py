from fastapi import HTTPException, status

from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.line_mappings import (
    LineMappingCreateRequest,
    LineMappingResponse,
    LineUnmapRequest,
    LineUnmapResponse,
)


class LineMappingService:
    def __init__(self, contract_repo: ContractRepository, line_mapping_repo: LineMappingRepository) -> None:
        self.contract_repo = contract_repo
        self.line_mapping_repo = line_mapping_repo

    async def map_line_user(self, payload: LineMappingCreateRequest) -> LineMappingResponse:
        contract = await self.contract_repo.get_by_contract_no(payload.contract_no)
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found.")

        existing_contract_mapping = await self.line_mapping_repo.get_active_by_contract_no(payload.contract_no)
        if existing_contract_mapping:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This contract is already mapped.")

        existing_line_mapping = await self.line_mapping_repo.get_active_by_line_user_id(payload.line_user_id)
        if existing_line_mapping:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This LINE user is already mapped.")

        entity = await self.line_mapping_repo.create(
            contract_no=payload.contract_no,
            customer_id=contract.customer_id,
            line_user_id=payload.line_user_id,
            line_display_name=payload.line_display_name,
            created_by=payload.created_by,
        )
        return LineMappingResponse(
            mapping_id=entity.id,
            contract_no=entity.contract_no,
            customer_id=entity.customer_id,
            line_user_id=entity.line_user_id,
            line_display_name=entity.line_display_name,
            map_status=entity.map_status,
            verified_flag=entity.verified_flag,
            mapped_at=entity.mapped_at,
        )

    async def unmap_line_user(self, payload: LineUnmapRequest) -> LineUnmapResponse:
        mapping = await self.line_mapping_repo.get_active_by_line_user_id(payload.line_user_id)
        if not mapping:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active LINE mapping not found.")
        await self.line_mapping_repo.unmap(mapping)
        return LineUnmapResponse(
            success=True,
            line_user_id=payload.line_user_id,
            contract_no=mapping.contract_no,
            message="LINE mapping has been removed successfully.",
        )
