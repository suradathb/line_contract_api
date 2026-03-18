from fastapi import HTTPException, status

import csv
import io
from decimal import Decimal, InvalidOperation
from app.repositories.contract_repository import ContractRepository
from app.schemas.contracts import ContractResponse, ContractImportRequest, ContractImportResponse, ContractImportCsvResult


class ContractService:
    def __init__(self, contract_repo: ContractRepository) -> None:
        self.contract_repo = contract_repo

    async def get_contract_by_line_user_id(self, line_user_id: str) -> ContractResponse:
        contract = await self.contract_repo.get_by_line_user_id(line_user_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found for this LINE user.",
            )

        return ContractResponse(
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            contract_status=contract.contract_status,
            total_outstanding_amount=contract.total_outstanding_amount,
            line_user_id=contract.line_user_id,
            line_display_name=contract.line_display_name,
            line_map_status=contract.line_map_status,
        )

    async def get_contract_by_contract_no(self, contract_no: str) -> ContractResponse:
        contract = await self.contract_repo.get_by_contract_no(contract_no)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found.",
            )

        return ContractResponse(
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            contract_status=contract.contract_status,
            total_outstanding_amount=contract.total_outstanding_amount,
            line_user_id=contract.line_user_id,
            line_display_name=contract.line_display_name,
            line_map_status=contract.line_map_status,
        )
    
    async def import_contracts(self, payload: ContractImportRequest):
        inserted = 0
        updated = 0

        for item in payload.contracts:
            result = await self.repo.upsert_contract(
                contract_no=item.contract_no,
                customer_name=item.customer_name,
                contract_status=item.contract_status,
                total_outstanding_amount=item.total_outstanding_amount,
            )

            if result == "inserted":
                inserted += 1
            else:
                updated += 1

        return ContractImportResponse(
            success=True,
            inserted=inserted,
            updated=updated,
            total=len(payload.contracts),
        )
    
    async def import_contracts_csv(self, content: bytes) -> ContractImportCsvResult:
            inserted = 0
            updated = 0
            failed = 0
            errors: list[str] = []

            try:
                text = content.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = content.decode("utf-8")

            reader = csv.DictReader(io.StringIO(text))

            required_columns = {
                "contract_no",
                "customer_name",
                "contract_status",
                "total_outstanding_amount",
            }

            if not reader.fieldnames:
                return ContractImportCsvResult(
                    success=False,
                    inserted=0,
                    updated=0,
                    failed=0,
                    total=0,
                    message="CSV file is empty or header is missing.",
                    errors=["CSV file is empty or header is missing."],
                )

            missing_columns = required_columns - set(reader.fieldnames)
            if missing_columns:
                return ContractImportCsvResult(
                    success=False,
                    inserted=0,
                    updated=0,
                    failed=0,
                    total=0,
                    message="CSV header is invalid.",
                    errors=[f"Missing columns: {', '.join(sorted(missing_columns))}"],
                )

            total = 0

            for row_number, row in enumerate(reader, start=2):
                total += 1
                try:
                    contract_no = (row.get("contract_no") or "").strip()
                    customer_name = (row.get("customer_name") or "").strip()
                    contract_status = (row.get("contract_status") or "").strip().upper()
                    total_outstanding_raw = (row.get("total_outstanding_amount") or "").strip()

                    if not contract_no:
                        raise ValueError("contract_no is required")
                    if not customer_name:
                        raise ValueError("customer_name is required")
                    if not contract_status:
                        raise ValueError("contract_status is required")

                    try:
                        total_outstanding_amount = Decimal(total_outstanding_raw)
                    except (InvalidOperation, TypeError):
                        raise ValueError("total_outstanding_amount must be a valid decimal")

                    result = await self.contract_repo.upsert_contract_master(
                        contract_no=contract_no,
                        customer_name=customer_name,
                        contract_status=contract_status,
                        total_outstanding_amount=total_outstanding_amount,
                    )

                    if result == "inserted":
                        inserted += 1
                    else:
                        updated += 1

                except Exception as exc:
                    failed += 1
                    errors.append(f"Row {row_number}: {str(exc)}")

            return ContractImportCsvResult(
                success=failed == 0,
                inserted=inserted,
                updated=updated,
                failed=failed,
                total=total,
                message="Contract CSV import completed." if failed == 0 else "Contract CSV import completed with errors.",
                errors=errors,
            )