from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PaymentSchedule


class PaymentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_latest_inquiry_by_contract_no(self, contract_no: str) -> PaymentSchedule | None:
        result = await self.db.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.contract_no == contract_no)
            .order_by(PaymentSchedule.installment_no.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history_by_contract_no(self, contract_no: str) -> list[PaymentSchedule]:
        result = await self.db.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.contract_no == contract_no)
            .order_by(PaymentSchedule.installment_no.asc())
        )
        return list(result.scalars().all())
