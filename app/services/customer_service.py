from app.repositories.contract_repository import ContractRepository
from app.repositories.line_mapping_repository import LineMappingRepository
from app.schemas.customers import CustomerVerifyRequest, CustomerVerifyResponse


class CustomerService:
    def __init__(
        self,
        contract_repo: ContractRepository,
        line_mapping_repo: LineMappingRepository,
    ) -> None:
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

        is_match = (
            contract.id_card_no == payload.id_card_no
            and contract.mobile_no == payload.mobile_no
        )
        if not is_match:
            return CustomerVerifyResponse(
                verified=False,
                contract_no=contract.contract_no,
                customer_id=contract.customer_id,
                customer_name=contract.customer_name,
                mobile_no=contract.mobile_no,
                vehicle_no=contract.vehicle_no,
                vehicle_type=contract.vehicle_type,
                contract_status=contract.contract_status,
                contract_start_date=contract.contract_start_date,
                contract_end_date=contract.contract_end_date,
                total_paid_amount=contract.total_paid_amount,
                total_outstanding_amount=contract.total_outstanding_amount,
                last_payment_date=contract.last_payment_date,
                line_notify_enabled=contract.line_notify_enabled,
                eligible_to_map=False,
                message="Customer verification failed.",
            )

        existing_contract_mapping = await self.line_mapping_repo.get_active_by_contract_no(
            contract.contract_no
        )
        if existing_contract_mapping:
            same_line_user = (
                payload.line_user_id is not None
                and existing_contract_mapping.line_user_id == payload.line_user_id
            )
            return CustomerVerifyResponse(
                verified=True,
                contract_no=contract.contract_no,
                customer_id=contract.customer_id,
                customer_name=contract.customer_name,
                mobile_no=contract.mobile_no,
                vehicle_no=contract.vehicle_no,
                vehicle_type=contract.vehicle_type,
                contract_status=contract.contract_status,
                contract_start_date=contract.contract_start_date,
                contract_end_date=contract.contract_end_date,
                total_paid_amount=contract.total_paid_amount,
                total_outstanding_amount=contract.total_outstanding_amount,
                last_payment_date=contract.last_payment_date,
                line_notify_enabled=contract.line_notify_enabled,
                eligible_to_map=False,
                message=(
                    "Customer verified and this contract is already mapped to this LINE user."
                    if same_line_user
                    else "Customer verified but contract is already mapped."
                ),
            )

        if payload.line_user_id:
            existing_line_mapping = await self.line_mapping_repo.get_active_by_line_user_id(
                payload.line_user_id
            )
            if existing_line_mapping:
                return CustomerVerifyResponse(
                    verified=False,
                    contract_no=contract.contract_no,
                    customer_id=contract.customer_id,
                    customer_name=contract.customer_name,
                    mobile_no=contract.mobile_no,
                    vehicle_no=contract.vehicle_no,
                    vehicle_type=contract.vehicle_type,
                    contract_status=contract.contract_status,
                    contract_start_date=contract.contract_start_date,
                    contract_end_date=contract.contract_end_date,
                    total_paid_amount=contract.total_paid_amount,
                    total_outstanding_amount=contract.total_outstanding_amount,
                    last_payment_date=contract.last_payment_date,
                    line_notify_enabled=contract.line_notify_enabled,
                    eligible_to_map=False,
                    message="This LINE user is already mapped to another contract.",
                )

        return CustomerVerifyResponse(
            verified=True,
            contract_no=contract.contract_no,
            customer_id=contract.customer_id,
            customer_name=contract.customer_name,
            mobile_no=contract.mobile_no,
            vehicle_no=contract.vehicle_no,
            vehicle_type=contract.vehicle_type,
            contract_status=contract.contract_status,
            contract_start_date=contract.contract_start_date,
            contract_end_date=contract.contract_end_date,
            total_paid_amount=contract.total_paid_amount,
            total_outstanding_amount=contract.total_outstanding_amount,
            last_payment_date=contract.last_payment_date,
            line_notify_enabled=contract.line_notify_enabled,
            eligible_to_map=True,
            message="Customer verified and eligible to map.",
        )