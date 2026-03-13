from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contract, PaymentSchedule


async def seed_demo_data(db: AsyncSession) -> None:
    result = await db.execute(select(func.count()).select_from(Contract))
    count = result.scalar_one()
    if count and count > 0:
        return

    contracts = [
        Contract(
            contract_no="EV0001",
            customer_id="CUST0001",
            id_card_no="1103700000011",
            customer_name="Alisa S.",
            mobile_no="0811111111",
            installment_amount=Decimal("666.00"),
            due_date=date(2026, 3, 31),
            contract_status="Active",
        ),
        Contract(
            contract_no="EV0002",
            customer_id="CUST0002",
            id_card_no="1103700000022",
            customer_name="Bob K.",
            mobile_no="0822222222",
            installment_amount=Decimal("777.00"),
            due_date=date(2026, 3, 31),
            contract_status="Active",
        ),
        Contract(
            contract_no="EV0003",
            customer_id="CUST0003",
            id_card_no="1103700000033",
            customer_name="Jon T.",
            mobile_no="0833333333",
            installment_amount=Decimal("888.00"),
            due_date=date(2026, 3, 31),
            contract_status="Active",
        ),
    ]
    db.add_all(contracts)
    await db.flush()

    payments = [
        PaymentSchedule(contract_no="EV0001", installment_no=1, due_date=date(2026, 1, 31), due_amount=Decimal("666.00"), paid_amount=Decimal("666.00"), outstanding_amount=Decimal("0.00"), payment_status="PAID", payment_date=date(2026, 1, 28), receipt_no="RCPT-0001"),
        PaymentSchedule(contract_no="EV0001", installment_no=2, due_date=date(2026, 2, 28), due_amount=Decimal("666.00"), paid_amount=Decimal("666.00"), outstanding_amount=Decimal("0.00"), payment_status="PAID", payment_date=date(2026, 2, 27), receipt_no="RCPT-0002"),
        PaymentSchedule(contract_no="EV0001", installment_no=3, due_date=date(2026, 3, 31), due_amount=Decimal("666.00"), paid_amount=Decimal("0.00"), outstanding_amount=Decimal("666.00"), payment_status="UNPAID", payment_date=None, receipt_no=None),
        PaymentSchedule(contract_no="EV0002", installment_no=1, due_date=date(2026, 1, 31), due_amount=Decimal("777.00"), paid_amount=Decimal("777.00"), outstanding_amount=Decimal("0.00"), payment_status="PAID", payment_date=date(2026, 1, 29), receipt_no="RCPT-0003"),
        PaymentSchedule(contract_no="EV0002", installment_no=2, due_date=date(2026, 2, 28), due_amount=Decimal("777.00"), paid_amount=Decimal("500.00"), outstanding_amount=Decimal("277.00"), payment_status="PARTIAL", payment_date=date(2026, 2, 26), receipt_no="RCPT-0004"),
        PaymentSchedule(contract_no="EV0002", installment_no=3, due_date=date(2026, 3, 31), due_amount=Decimal("777.00"), paid_amount=Decimal("0.00"), outstanding_amount=Decimal("777.00"), payment_status="UNPAID", payment_date=None, receipt_no=None),
        PaymentSchedule(contract_no="EV0003", installment_no=1, due_date=date(2026, 1, 31), due_amount=Decimal("888.00"), paid_amount=Decimal("888.00"), outstanding_amount=Decimal("0.00"), payment_status="PAID", payment_date=date(2026, 1, 30), receipt_no="RCPT-0005"),
        PaymentSchedule(contract_no="EV0003", installment_no=2, due_date=date(2026, 2, 28), due_amount=Decimal("888.00"), paid_amount=Decimal("888.00"), outstanding_amount=Decimal("0.00"), payment_status="PAID", payment_date=date(2026, 2, 28), receipt_no="RCPT-0006"),
        PaymentSchedule(contract_no="EV0003", installment_no=3, due_date=date(2026, 3, 31), due_amount=Decimal("888.00"), paid_amount=Decimal("300.00"), outstanding_amount=Decimal("588.00"), payment_status="PARTIAL", payment_date=date(2026, 3, 8), receipt_no="RCPT-0007"),
    ]
    db.add_all(payments)
    await db.commit()
