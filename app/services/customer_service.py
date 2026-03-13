from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.customers import CustomerVerifyRequest, CustomerVerifyResponse


class CustomerService:
    def __init__(self, contract_repo: ContractRepository, line_mapping_repo: LineMappingRepository) -> None:
        self.contract_repo = contract_repo
        self.line_mapping_repo = line_mapping_repo

    async def verify_customer(self, payload: CustomerVerifyRequest) -> CustomerVerifyResponse:
        contract = await self.contract_repo.get_by_contract_no(payload.contract_no)
        if not contract:
            return CustomerVerifyResponse(
                verified=False,
                contract_no=payload.contract_no,
                eligible_to_map=False,
                message="Contract not found.",
            )

        existing_contract_mapping = await self.line_mapping_repo.get_active_by_contract_no(contract.contract_no)
        if existing_contract_mapping:
            return CustomerVerifyResponse(
                verified=True,
                contract_no=contract.contract_no,
                customer_name=contract.customer_name,
                contract_status=contract.contract_status,
                eligible_to_map=False,
                message="Customer verified but contract is already mapped.",
            )

        existing_line_mapping = await self.line_mapping_repo.get_active_by_line_user_id(payload.line_user_id)
        if existing_line_mapping:
            return CustomerVerifyResponse(
                verified=False,
                contract_no=contract.contract_no,
                customer_name=contract.customer_name,
                contract_status=contract.contract_status,
                eligible_to_map=False,
                message="This LINE user is already mapped to another contract.",
            )

        return CustomerVerifyResponse(
            verified=True,
            contract_no=contract.contract_no,
            customer_name=contract.customer_name,
            contract_status=contract.contract_status,
            eligible_to_map=True,
            message="Customer verified and eligible to map.",
        )