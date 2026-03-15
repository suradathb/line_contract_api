from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contract
from app.schemas.contracts import ContractCreateRequest, ContractUpdateRequest


class ContractRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_contract_no(self, contract_no: str) -> Contract | None:
        result = await self.db.execute(
            select(Contract).where(Contract.contract_no == contract_no)
        )
        return result.scalar_one_or_none()

    async def get_by_customer_id(self, customer_id: str) -> list[Contract]:
        result = await self.db.execute(
            select(Contract)
            .where(Contract.customer_id == customer_id)
            .order_by(Contract.contract_no.asc())
        )
        return list(result.scalars().all())

    async def create(self, payload: ContractCreateRequest) -> Contract:
        entity = Contract(
            contract_no=payload.contract_no,
            customer_id=payload.customer_id,
            id_card_no=payload.id_card_no,
            customer_name=payload.customer_name,
            mobile_no=payload.mobile_no,
            vehicle_no=payload.vehicle_no,
            vehicle_type=payload.vehicle_type,
            daily_rent_amount=payload.daily_rent_amount,
            deposit_amount=payload.deposit_amount,
            contract_start_date=payload.contract_start_date,
            contract_end_date=payload.contract_end_date,
            contract_status=payload.contract_status,
            total_paid_amount=payload.total_paid_amount,
            total_outstanding_amount=payload.total_outstanding_amount,
            last_payment_date=payload.last_payment_date,
            line_notify_enabled=payload.line_notify_enabled,
            remark=payload.remark,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: Contract, payload: ContractUpdateRequest) -> Contract:
        update_data = payload.model_dump(exclude_unset=True)

        for field_name, value in update_data.items():
            setattr(entity, field_name, value)

        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update_payment_summary(
        self,
        entity: Contract,
        total_paid_amount: Decimal,
        total_outstanding_amount: Decimal,
        last_payment_date,
    ) -> Contract:
        entity.total_paid_amount = total_paid_amount
        entity.total_outstanding_amount = total_outstanding_amount
        entity.last_payment_date = last_payment_date

        await self.db.flush()
        await self.db.refresh(entity)
        return entity