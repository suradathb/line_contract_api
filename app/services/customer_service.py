from app.repositories.contract_repository import ContractRepository
from app.schemas.customers import (
    CustomerMapRequest,
    CustomerMapResponse,
    CustomerUnmapResponse,
    CustomerVerifyRequest,
    CustomerVerifyResponse,
)


class CustomerService:
    def __init__(self, contract_repo: ContractRepository):
        self.contract_repo = contract_repo

    async def verify_customer(self, payload: CustomerVerifyRequest) -> CustomerVerifyResponse:
        contract = await self.contract_repo.get_by_contract_no(payload.contract_no)

        if not contract:
            return CustomerVerifyResponse(
                verified=False,
                contract_no=payload.contract_no,
                customer_name=None,
                contract_status=None,
                eligible_to_map=False,
                message="Contract not found.",
            )

        if contract.contract_status != "ACTIVE":
            return CustomerVerifyResponse(
                verified=True,
                contract_no=contract.contract_no,
                customer_name=contract.customer_name,
                contract_status=contract.contract_status,
                eligible_to_map=False,
                message="Contract is not active.",
            )

        if contract.line_user_id:
            return CustomerVerifyResponse(
                verified=True,
                contract_no=contract.contract_no,
                customer_name=contract.customer_name,
                contract_status=contract.contract_status,
                eligible_to_map=False,
                message="Contract is already mapped.",
            )

        return CustomerVerifyResponse(
            verified=True,
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            contract_status=contract.contract_status,
            eligible_to_map=True,
            message="Contract verified and eligible to map.",
        )

    async def map_customer(self, payload: CustomerMapRequest) -> CustomerMapResponse:
        contract = await self.contract_repo.get_by_contract_no(payload.contract_no)
        if not contract:
            raise ValueError("Contract not found.")

        if contract.contract_status != "ACTIVE":
            raise ValueError("Contract is not active.")

        if contract.line_user_id:
            raise ValueError("Contract is already mapped.")

        existed_line = await self.contract_repo.get_by_line_user_id(payload.line_user_id)
        if existed_line:
            raise ValueError("This LINE user is already mapped to another contract.")

        contract = await self.contract_repo.map_line(
            contract_no=payload.contract_no,
            line_user_id=payload.line_user_id,
            line_display_name=payload.line_display_name,
        )

        if not contract:
            raise ValueError("Contract not found.")

        return CustomerMapResponse(
            success=True,
            contract_no=contract.contract_no,
            line_user_id=contract.line_user_id or "",
            line_display_name=contract.line_display_name,
            message="Contract mapped successfully.",
        )

    async def unmap_customer(self, contract_no: str) -> CustomerUnmapResponse:
        contract = await self.contract_repo.get_by_contract_no(contract_no)
        if not contract:
            raise ValueError("Contract not found.")

        if not contract.line_user_id:
            return CustomerUnmapResponse(
                success=True,
                contract_no=contract.contract_no,
                message="Contract is already unmapped.",
            )

        contract = await self.contract_repo.unmap_line(contract_no)
        if not contract:
            raise ValueError("Contract not found.")

        return CustomerUnmapResponse(
            success=True,
            contract_no=contract.contract_no,
            message="Contract unmapped successfully.",
        )