import json
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApiLog


class ApiLogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        api_name: str,
        response_code: str,
        contract_no: str | None = None,
        line_user_id: str | None = None,
        api_direction: str | None = None,
        source_system: str | None = None,
        target_system: str | None = None,
        request_payload: dict | list | None = None,
        response_payload: dict | list | None = None,
        error_message: str | None = None,
        request_ref: str | None = None,
    ) -> ApiLog:
        entity = ApiLog(
            api_name=api_name,
            request_ref=request_ref or str(uuid4()),
            contract_no=contract_no,
            line_user_id=line_user_id,
            api_direction=api_direction,
            source_system=source_system,
            target_system=target_system,
            request_payload=json.dumps(request_payload, default=str) if request_payload is not None else None,
            response_payload=json.dumps(response_payload, default=str) if response_payload is not None else None,
            response_code=response_code,
            error_message=error_message,
        )
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity