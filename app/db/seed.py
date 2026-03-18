from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract_master import ContractMaster


async def seed_demo_data(db: AsyncSession) -> None:
    result = await db.execute(select(func.count()).select_from(ContractMaster))
    count = result.scalar_one()
    if count and count > 0:
        return

    contracts = [
        ContractMaster(
            contract_no="EV0001",
            customer_name="Alisa S.",
            contract_status="ACTIVE",
            total_outstanding_amount=Decimal("666.00"),
            line_user_id="U_DEMO_0001",
            line_display_name="Alisa Line",
            line_map_status="ACTIVE",
            line_notify_enabled=True,
            line_mapped_at=datetime.utcnow(),
        ),
        ContractMaster(
            contract_no="EV0002",
            customer_name="Bob K.",
            contract_status="ACTIVE",
            total_outstanding_amount=Decimal("1054.00"),
            line_user_id="U_DEMO_0002",
            line_display_name="Bob Line",
            line_map_status="ACTIVE",
            line_notify_enabled=True,
            line_mapped_at=datetime.utcnow(),
        ),
        ContractMaster(
            contract_no="EV0003",
            customer_name="Jon T.",
            contract_status="ACTIVE",
            total_outstanding_amount=Decimal("588.00"),
            line_user_id=None,
            line_display_name=None,
            line_map_status="UNMAPPED",
            line_notify_enabled=False,
            line_mapped_at=None,
        ),
    ]

    db.add_all(contracts)
    await db.commit()