import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException, status

from app.repositories.contract_repository import ContractRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.payments import (
    MarkPaymentSentResponse,
    NextPaymentToSendResponse,
    PaymentHistoryItemResponse,
    PaymentImportResult,
    PaymentInquiryResponse,
    PaymentScheduleResponse,
)


class PaymentService:
    def __init__(
        self,
        contract_repo: ContractRepository,
        payment_repo: PaymentRepository,
    ):
        self.contract_repo = contract_repo
        self.payment_repo = payment_repo

    async def get_payment_inquiry_by_line_user_id(
        self,
        line_user_id: str,
        billing_date: date,
    ) -> PaymentInquiryResponse:
        contract = await self.contract_repo.get_by_line_user_id(line_user_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LINE user is not mapped to any contract.",
            )

        payment = await self.payment_repo.get_inquiry_by_contract_no_and_billing_date(
            contract.contract_no,
            billing_date,
        )
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment information not found for billing_date {billing_date.isoformat()}.",
            )

        return PaymentInquiryResponse(
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            billing_seq=payment.billing_seq,
            billing_date=payment.billing_date,
            daily_rent_amount=payment.daily_rent_amount,
            paid_amount=payment.paid_amount,
            outstanding_amount=payment.outstanding_amount,
            payment_status=payment.payment_status,
            payment_date=payment.payment_date,
            receipt_no=payment.receipt_no,
            remark=payment.remark,
        )

    async def get_payment_history_by_line_user_id(
        self,
        line_user_id: str,
    ) -> list[PaymentHistoryItemResponse]:
        contract = await self.contract_repo.get_by_line_user_id(line_user_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LINE user is not mapped to any contract.",
            )

        history = await self.payment_repo.get_history_by_contract_no(contract.contract_no)
        return [
            PaymentHistoryItemResponse.model_validate(item, from_attributes=True)
            for item in history
        ]

    def _parse_date(self, value: str, field_name: str) -> date:
        try:
            return date.fromisoformat((value or "").strip())
        except Exception as exc:
            raise ValueError(f"Invalid {field_name}: {value}. Expected YYYY-MM-DD") from exc

    def _parse_optional_date(self, value: str) -> date | None:
        value = (value or "").strip()
        if not value:
            return None
        return self._parse_date(value, "payment_date")

    def _parse_decimal(self, value: str, field_name: str) -> Decimal:
        try:
            return Decimal((value or "").strip())
        except (InvalidOperation, AttributeError) as exc:
            raise ValueError(f"Invalid decimal for {field_name}: {value}") from exc

    def _parse_bool(self, value: str, field_name: str) -> bool:
        normalized = (value or "").strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n", ""}:
            return False
        raise ValueError(f"Invalid boolean for {field_name}: {value}")

    async def import_payment_schedules_csv(self, content: bytes) -> PaymentImportResult:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        required_headers = {
            "contract_no",
            "billing_seq",
            "billing_date",
            "daily_rent_amount",
            "paid_amount",
            "outstanding_amount",
            "payment_status",
            "payment_date",
            "receipt_no",
            "sent_line_flag",
            "remark",
        }

        actual_headers = set(reader.fieldnames or [])
        missing_headers = required_headers - actual_headers
        if missing_headers:
            return PaymentImportResult(
                total_rows=0,
                success_rows=0,
                failed_rows=0,
                errors=[f"Missing CSV headers: {', '.join(sorted(missing_headers))}"],
            )

        total_rows = 0
        success_rows = 0
        failed_rows = 0
        errors: list[str] = []

        for row_index, row in enumerate(reader, start=2):
            total_rows += 1
            try:
                contract_no = (row.get("contract_no") or "").strip()
                if not contract_no:
                    raise ValueError("contract_no is required")

                contract = await self.contract_repo.get_by_contract_no(contract_no)
                if not contract:
                    raise ValueError(f"Contract not found: {contract_no}")

                billing_seq_raw = (row.get("billing_seq") or "").strip()
                if not billing_seq_raw:
                    raise ValueError("billing_seq is required")
                billing_seq = int(billing_seq_raw)

                billing_date = self._parse_date(row.get("billing_date", ""), "billing_date")
                daily_rent_amount = self._parse_decimal(
                    row.get("daily_rent_amount", "0"),
                    "daily_rent_amount",
                )
                paid_amount = self._parse_decimal(
                    row.get("paid_amount", "0"),
                    "paid_amount",
                )
                outstanding_amount = self._parse_decimal(
                    row.get("outstanding_amount", "0"),
                    "outstanding_amount",
                )

                payment_status = (row.get("payment_status") or "UNPAID").strip().upper()
                payment_date = self._parse_optional_date(row.get("payment_date", ""))
                receipt_no = (row.get("receipt_no") or "").strip() or None
                sent_line_flag = self._parse_bool(
                    row.get("sent_line_flag", "false"),
                    "sent_line_flag",
                )
                remark = (row.get("remark") or "").strip() or None

                await self.payment_repo.upsert_payment_schedule(
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
                    remark=remark,
                )
                success_rows += 1
            except Exception as exc:
                failed_rows += 1
                errors.append(f"Row {row_index}: {exc}")

        return PaymentImportResult(
            total_rows=total_rows,
            success_rows=success_rows,
            failed_rows=failed_rows,
            errors=errors,
        )

    async def export_payment_schedules_csv(self, contract_no: str | None = None) -> str:
        rows = await self.payment_repo.list_for_export(contract_no=contract_no)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "contract_no",
                "billing_seq",
                "billing_date",
                "daily_rent_amount",
                "paid_amount",
                "outstanding_amount",
                "payment_status",
                "payment_date",
                "receipt_no",
                "sent_line_flag",
                "sent_line_at",
                "remark",
                "created_at",
                "updated_at",
            ]
        )

        for row in rows:
            writer.writerow(
                [
                    row.id,
                    row.contract_no,
                    row.billing_seq,
                    row.billing_date.isoformat(),
                    str(row.daily_rent_amount),
                    str(row.paid_amount),
                    str(row.outstanding_amount),
                    row.payment_status,
                    row.payment_date.isoformat() if row.payment_date else "",
                    row.receipt_no or "",
                    str(row.sent_line_flag).lower(),
                    row.sent_line_at.isoformat() if row.sent_line_at else "",
                    row.remark or "",
                    row.created_at.isoformat(),
                    row.updated_at.isoformat(),
                ]
            )

        return output.getvalue()

    async def get_next_payment_to_send(self, contract_no: str) -> NextPaymentToSendResponse:
        contract = await self.contract_repo.get_by_contract_no(contract_no)
        if not contract:
            return NextPaymentToSendResponse(
                contract_no=contract_no,
                has_active_mapping=False,
                payment=None,
                message="Contract not found.",
            )

        has_active_mapping = bool(contract.line_user_id)

        if not has_active_mapping:
            return NextPaymentToSendResponse(
                contract_no=contract_no,
                has_active_mapping=False,
                payment=None,
                message="Contract exists but has no active LINE mapping.",
            )

        payment = await self.payment_repo.get_next_to_send(contract_no)
        if not payment:
            return NextPaymentToSendResponse(
                contract_no=contract_no,
                has_active_mapping=True,
                line_user_id=contract.line_user_id,
                line_display_name=contract.line_display_name,
                payment=None,
                message="No pending payment to send.",
            )

        return NextPaymentToSendResponse(
            contract_no=contract_no,
            has_active_mapping=True,
            line_user_id=contract.line_user_id,
            line_display_name=contract.line_display_name,
            payment=PaymentScheduleResponse.model_validate(payment, from_attributes=True),
            message="Next payment to send found.",
        )

    async def mark_payment_sent(self, payment_id: int) -> MarkPaymentSentResponse:
        payment = await self.payment_repo.get_by_id(payment_id)
        if not payment:
            raise ValueError(f"PaymentSchedule not found: {payment_id}")

        updated = await self.payment_repo.mark_sent(payment)

        return MarkPaymentSentResponse(
            payment_id=updated.id,
            contract_no=updated.contract_no,
            sent_line_flag=updated.sent_line_flag,
            sent_line_at=updated.sent_line_at,
        )