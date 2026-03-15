from datetime import date
from decimal import Decimal

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
            .order_by(PaymentSchedule.billing_seq.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history_by_contract_no(self, contract_no: str) -> list[PaymentSchedule]:
        result = await self.db.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.contract_no == contract_no)
            .order_by(PaymentSchedule.billing_seq.asc())
        )
        return list(result.scalars().all())

    async def get_by_contract_no_and_billing_seq(
        self,
        contract_no: str,
        billing_seq: int,
    ) -> PaymentSchedule | None:
        result = await self.db.execute(
            select(PaymentSchedule).where(
                PaymentSchedule.contract_no == contract_no,
                PaymentSchedule.billing_seq == billing_seq,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_contract_no_and_billing_date(
        self,
        contract_no: str,
        billing_date: date,
    ) -> PaymentSchedule | None:
        result = await self.db.execute(
            select(PaymentSchedule).where(
                PaymentSchedule.contract_no == contract_no,
                PaymentSchedule.billing_date == billing_date,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        contract_no: str,
        billing_seq: int,
        billing_date: date,
        daily_rent_amount: Decimal,
        paid_amount: Decimal,
        outstanding_amount: Decimal,
        payment_status: str = "UNPAID",
        payment_date: date | None = None,
        receipt_no: str | None = None,
        sent_line_flag: bool = False,
        sent_line_at=None,
        remark: str | None = None,
    ) -> PaymentSchedule:
        entity = PaymentSchedule(
            contract_no=contract_no,
            billing_seq=billing_seq,
            billing_date=billing_date,
            daily_rent_amount=daily_rent_amount,
            paid_amount=paid_amount,
            outstanding_amount=outstanding_amount,
            payment_status=payment_status,
            payment_date=payment_date,
            receipt_no=receipt_no,
            sent_line_flag=sent_line_flag,
            sent_line_at=sent_line_at,
            remark=remark,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update_payment(
        self,
        entity: PaymentSchedule,
        paid_amount: Decimal,
        outstanding_amount: Decimal,
        payment_status: str,
        payment_date: date | None,
        receipt_no: str | None,
        remark: str | None = None,
    ) -> PaymentSchedule:
        entity.paid_amount = paid_amount
        entity.outstanding_amount = outstanding_amount
        entity.payment_status = payment_status
        entity.payment_date = payment_date
        entity.receipt_no = receipt_no

        if remark is not None:
            entity.remark = remark

        await self.db.flush()
        await self.db.refresh(entity)
        return entity