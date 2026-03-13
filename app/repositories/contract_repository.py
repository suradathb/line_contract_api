from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contract


class ContractRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_contract_no(self, contract_no: str) -> Contract | None:
        result = await self.db.execute(select(Contract).where(Contract.contract_no == contract_no))
        return result.scalar_one_or_none()
