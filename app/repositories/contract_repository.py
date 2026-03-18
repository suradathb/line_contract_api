from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract_master import ContractMaster


class ContractRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_contract_no(self, contract_no: str) -> ContractMaster | None:
        result = await self.db.execute(
            select(ContractMaster).where(ContractMaster.contract_no == contract_no)
        )
        return result.scalar_one_or_none()

    async def get_by_line_user_id(self, line_user_id: str) -> ContractMaster | None:
        result = await self.db.execute(
            select(ContractMaster).where(ContractMaster.line_user_id == line_user_id)
        )
        return result.scalar_one_or_none()

    async def map_line(
        self,
        contract_no: str,
        line_user_id: str,
        line_display_name: str | None = None,
    ) -> ContractMaster | None:
        contract = await self.get_by_contract_no(contract_no)
        if not contract:
            return None

        contract.line_user_id = line_user_id
        contract.line_display_name = line_display_name
        contract.line_map_status = "ACTIVE"
        contract.line_notify_enabled = True
        contract.line_mapped_at = datetime.utcnow()

        await self.db.flush()
        return contract

    async def unmap_line(self, contract_no: str) -> ContractMaster | None:
        contract = await self.get_by_contract_no(contract_no)
        if not contract:
            return None

        contract.line_user_id = None
        contract.line_display_name = None
        contract.line_map_status = "UNMAPPED"
        contract.line_notify_enabled = False
        contract.line_mapped_at = None

        await self.db.flush()
        return contract
    
    async def upsert_contract(
        self,
        contract_no: str,
        customer_name: str,
        contract_status: str,
        total_outstanding_amount,
    ):
        contract = await self.get_by_contract_no(contract_no)

        if contract:
            # update
            contract.customer_name = customer_name
            contract.contract_status = contract_status
            contract.total_outstanding_amount = total_outstanding_amount
            return "updated"

        # insert ใหม่
        new_contract = ContractMaster(
            contract_no=contract_no,
            customer_name=customer_name,
            contract_status=contract_status,
            total_outstanding_amount=total_outstanding_amount,
            line_user_id=None,
            line_display_name=None,
            line_map_status="UNMAPPED",
            line_notify_enabled=False,
            line_mapped_at=None,
        )

        self.db.add(new_contract)
        return "inserted"