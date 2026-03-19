from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.contract_repository import ContractRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.line_messaging import LinePushMenuRequest, LinePushTextRequest
from app.services.line_messaging_service import LineMessagingService

router = APIRouter(prefix="/line", tags=["LINE Messaging"])


@router.get("/webhook/health")
async def line_webhook_health() -> dict:
    return {"message": "LINE webhook endpoint is ready"}


@router.post("/webhook")
async def line_webhook_callback(
    request: Request,
    x_line_signature: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    raw_body = await request.body()

    service = LineMessagingService()

    if not service.verify_signature(raw_body, x_line_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid LINE signature.",
        )

    payload = await request.json()
    events = payload.get("events", [])

    contract_repo = ContractRepository(db)
    payment_repo = PaymentRepository(db)

    for event in events:
        event_type = event.get("type")
        source = event.get("source", {})
        line_user_id = source.get("userId")
        reply_token = event.get("replyToken")

        if event_type == "follow" and reply_token and line_user_id:
            await service.handle_follow_event(
                reply_token=reply_token,
                line_user_id=line_user_id,
            )
            continue

        if event_type == "message" and reply_token:
            await service.handle_message_event(
                event=event,
                contract_repo=contract_repo,
                payment_repo=payment_repo,
            )
            continue

        if event_type == "postback" and reply_token:
            await service.handle_postback_event(
                event=event,
                contract_repo=contract_repo,
                payment_repo=payment_repo,
            )
            continue

    return {"ok": True}


@router.post("/test/push-text")
async def test_push_text(
    payload: LinePushTextRequest,
) -> dict:
    service = LineMessagingService()
    result = await service.push_text(payload.line_user_id, payload.text)
    return {"message": "Push text sent", "result": result}


@router.post("/test/push-menu")
async def test_push_menu(
    payload: LinePushMenuRequest,
) -> dict:
    service = LineMessagingService()
    result = await service.push_messages(
        payload.line_user_id,
        [
            {
                "type": "template",
                "altText": "เมนูทดสอบ LINE Contract API",
                "template": {
                    "type": "buttons",
                    "title": "LINE Contract API",
                    "text": "เลือก action ที่ต้องการทดสอบ",
                    "actions": [
                        {
                            "type": "postback",
                            "label": "เช็คยอดวันนี้",
                            "data": "action=payment_inquiry_today",
                            "displayText": "เช็คยอดวันนี้",
                        },
                        {
                            "type": "message",
                            "label": "เช็คยอดระบุวันที่",
                            "text": "ยอด 2026-03-19",
                        },
                        {
                            "type": "message",
                            "label": "Ping",
                            "text": "ping",
                        },
                        {
                            "type": "message",
                            "label": "Help",
                            "text": "help",
                        },
                    ],
                },
            }
        ],
    )
    return {"message": "Push menu sent", "result": result}