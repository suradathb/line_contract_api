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

    async def get_by_contract_no(self, contract_no: str) -> list[LineMapping]:
        result = await self.db.execute(
            select(LineMapping)
            .where(LineMapping.contract_no == contract_no)
            .order_by(LineMapping.mapped_at.desc(), LineMapping.id.desc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        contract_no: str,
        customer_id: str,
        line_user_id: str,
        line_display_name: str | None,
        line_picture_url: str | None,
        created_by: str,
        remark: str | None = None,
    ) -> LineMapping:
        entity = LineMapping(
            contract_no=contract_no,
            customer_id=customer_id,
            line_user_id=line_user_id,
            line_display_name=line_display_name,
            line_picture_url=line_picture_url,
            map_status="ACTIVE",
            verified_flag=True,
            mapped_at=datetime.utcnow(),
            created_by=created_by,
            remark=remark,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def unmap(
        self,
        entity: LineMapping,
        remark: str | None = None,
    ) -> LineMapping:
        entity.map_status = "INACTIVE"
        entity.unmapped_at = datetime.utcnow()

        if remark is not None:
            entity.remark = remark

        await self.db.flush()
        await self.db.refresh(entity)
        return entity