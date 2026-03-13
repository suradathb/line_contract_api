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
        request_payload: dict | None = None,
        response_payload: dict | list | None = None,
        error_message: str | None = None,
    ) -> ApiLog:
        entity = ApiLog(
            api_name=api_name,
            request_ref=str(uuid4()),
            contract_no=contract_no,
            line_user_id=line_user_id,
            request_payload=json.dumps(request_payload, default=str) if request_payload else None,
            response_payload=json.dumps(response_payload, default=str) if response_payload is not None else None,
            response_code=response_code,
            error_message=error_message,
        )
        self.db.add(entity)
        await self.db.flush()
        return entity
