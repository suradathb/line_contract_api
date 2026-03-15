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
    def __init__(
        self,
        contract_repo: ContractRepository,
        line_mapping_repo: LineMappingRepository,
    ) -> None:
        self.contract_repo = contract_repo
        self.line_mapping_repo = line_mapping_repo

    async def map_line_user(self, payload: LineMappingCreateRequest) -> LineMappingResponse:
        contract = await self.contract_repo.get_by_contract_no(payload.contract_no)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found.",
            )

        existing_contract_mapping = await self.line_mapping_repo.get_active_by_contract_no(
            payload.contract_no
        )
        if existing_contract_mapping:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This contract is already mapped.",
            )

        existing_line_mapping = await self.line_mapping_repo.get_active_by_line_user_id(
            payload.line_user_id
        )
        if existing_line_mapping:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This LINE user is already mapped.",
            )

        entity = await self.line_mapping_repo.create(
            contract_no=payload.contract_no,
            customer_id=contract.customer_id,
            line_user_id=payload.line_user_id,
            line_display_name=payload.line_display_name,
            line_picture_url=payload.line_picture_url,
            created_by=payload.created_by,
            remark=payload.remark,
        )

        return LineMappingResponse.model_validate(entity, from_attributes=True)

    async def unmap_line_user(self, payload: LineUnmapRequest) -> LineUnmapResponse:
        mapping = await self.line_mapping_repo.get_active_by_line_user_id(payload.line_user_id)
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active LINE mapping not found.",
            )

        if payload.contract_no and mapping.contract_no != payload.contract_no:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LINE user ID does not match the specified contract.",
            )

        updated_mapping = await self.line_mapping_repo.unmap(mapping, remark=payload.remark)

        return LineUnmapResponse(
            success=True,
            line_user_id=updated_mapping.line_user_id,
            contract_no=updated_mapping.contract_no,
            map_status=updated_mapping.map_status,
            unmapped_at=updated_mapping.unmapped_at,
            message="LINE mapping has been removed successfully.",
        )