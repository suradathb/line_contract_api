from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LineMapping


class LineMappingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_active_by_contract_no(self, contract_no: str) -> LineMapping | None:
        result = await self.db.execute(
            select(LineMapping).where(
                LineMapping.contract_no == contract_no,
                LineMapping.map_status == "ACTIVE",
            )
        )
        return result.scalar_one_or_none()

    async def get_active_by_line_user_id(self, line_user_id: str) -> LineMapping | None:
        result = await self.db.execute(
            select(LineMapping).where(
                LineMapping.line_user_id == line_user_id,
                LineMapping.map_status == "ACTIVE",
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        contract_no: str,
        customer_id: str,
        line_user_id: str,
        line_display_name: str | None,
        created_by: str,
    ) -> LineMapping:
        entity = LineMapping(
            contract_no=contract_no,
            customer_id=customer_id,
            line_user_id=line_user_id,
            line_display_name=line_display_name,
            map_status="ACTIVE",
            verified_flag=True,
            created_by=created_by,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def unmap(self, entity: LineMapping) -> LineMapping:
        entity.map_status = "INACTIVE"
        entity.unmapped_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
