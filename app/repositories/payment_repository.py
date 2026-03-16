from datetime import date, datetime
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

    async def get_by_id(self, payment_id: int) -> PaymentSchedule | None:
        result = await self.db.execute(
            select(PaymentSchedule).where(PaymentSchedule.id == payment_id)
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

    async def upsert_payment_schedule(
        self,
        *,
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
        remark: str | None = None,
    ) -> PaymentSchedule:
        entity = await self.get_by_contract_no_and_billing_date(contract_no, billing_date)

        if entity:
            entity.billing_seq = billing_seq
            entity.daily_rent_amount = daily_rent_amount
            entity.paid_amount = paid_amount
            entity.outstanding_amount = outstanding_amount
            entity.payment_status = payment_status
            entity.payment_date = payment_date
            entity.receipt_no = receipt_no
            entity.sent_line_flag = sent_line_flag
            entity.remark = remark
            entity.updated_at = datetime.utcnow()

            if sent_line_flag and entity.sent_line_at is None:
                entity.sent_line_at = datetime.utcnow()

            if not sent_line_flag:
                entity.sent_line_at = None

            await self.db.flush()
            await self.db.refresh(entity)
            return entity

        return await self.create(
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
            sent_line_at=datetime.utcnow() if sent_line_flag else None,
            remark=remark,
        )

    async def list_for_export(self, contract_no: str | None = None) -> list[PaymentSchedule]:
        stmt = select(PaymentSchedule)

        if contract_no:
            stmt = stmt.where(PaymentSchedule.contract_no == contract_no)

        stmt = stmt.order_by(PaymentSchedule.contract_no.asc(), PaymentSchedule.billing_date.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_next_to_send(self, contract_no: str) -> PaymentSchedule | None:
        result = await self.db.execute(
            select(PaymentSchedule)
            .where(
                PaymentSchedule.contract_no == contract_no,
                PaymentSchedule.outstanding_amount > 0,
                PaymentSchedule.payment_status.in_(["UNPAID", "PARTIAL"]),
                PaymentSchedule.sent_line_flag.is_(False),
            )
            .order_by(
                PaymentSchedule.billing_date.asc(),
                PaymentSchedule.billing_seq.asc(),
                PaymentSchedule.id.asc(),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def mark_sent(self, entity: PaymentSchedule) -> PaymentSchedule:
        entity.sent_line_flag = True
        entity.sent_line_at = datetime.utcnow()
        entity.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(entity)
        return entity