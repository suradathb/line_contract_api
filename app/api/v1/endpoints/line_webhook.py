from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.contract_repository import ContractRepository
from app.schemas.customers import CustomerMapRequest, CustomerVerifyRequest
from app.schemas.line_messaging import LinePushMenuRequest, LinePushTextRequest
from app.services.conversation_state import conversation_state_service
from app.services.customer_service import CustomerService
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

    line_service = LineMessagingService()

    if not line_service.verify_signature(raw_body, x_line_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid LINE signature.",
        )

    payload = await request.json()
    events = payload.get("events", [])

    contract_repo = ContractRepository(db)
    customer_service = CustomerService(contract_repo)

    for event in events:
        event_type = event.get("type")
        source = event.get("source", {})
        line_user_id = source.get("userId")
        reply_token = event.get("replyToken")

        if not line_user_id or not reply_token:
            continue

        # =========================================================
        # 1) POSTBACK จาก rich menu / ปุ่ม
        # =========================================================
        if event_type == "postback":
            postback = event.get("postback", {})
            data = (postback.get("data") or "").strip()

            if data == "action=map_contract":
                existing_contract = await contract_repo.get_by_line_user_id(line_user_id)

                if existing_contract:
                    conversation_state_service.clear_state(line_user_id)
                    await line_service.reply_text_message(
                        reply_token,
                        (
                            "LINE account นี้ผูกสัญญาไว้แล้ว\n"
                            f"เลขสัญญา: {existing_contract.contract_no}\n"
                            f"ลูกค้า: {existing_contract.customer_name}"
                        ),
                    )
                    continue

                conversation_state_service.set_state(line_user_id, "WAITING_CONTRACT_NO")
                await line_service.reply_text_message(
                    reply_token,
                    "กรุณาส่งเลขสัญญา เช่น EV0001",
                )
                continue

            if data == "action=cancel":
                conversation_state_service.clear_state(line_user_id)
                await line_service.reply_text_message(
                    reply_token,
                    "ยกเลิกรายการปัจจุบันแล้ว",
                )
                continue

        # =========================================================
        # 2) MESSAGE TEXT
        # =========================================================
        if event_type == "message":
            message = event.get("message", {})
            if message.get("type") != "text":
                continue

            text = (message.get("text") or "").strip()
            user_state = conversation_state_service.get_state(line_user_id)

            # -----------------------------------------------------
            # 2.1 ผู้ใช้พิมพ์ MAP เอง
            # -----------------------------------------------------
            if text.upper() == "MAP":
                existing_contract = await contract_repo.get_by_line_user_id(line_user_id)

                if existing_contract:
                    conversation_state_service.clear_state(line_user_id)
                    await line_service.reply_text_message(
                        reply_token,
                        (
                            "LINE account นี้ผูกสัญญาไว้แล้ว\n"
                            f"เลขสัญญา: {existing_contract.contract_no}\n"
                            # f"ลูกค้า: {existing_contract.customer_name}"
                        ),
                    )
                    continue

                conversation_state_service.set_state(line_user_id, "WAITING_CONTRACT_NO")
                await line_service.reply_text_message(
                    reply_token,
                    "กรุณาส่งเลขสัญญา เช่น EV0001",
                )
                continue

            # -----------------------------------------------------
            # 2.2 ผู้ใช้พิมพ์ CANCEL
            # -----------------------------------------------------
            if text.upper() in {"CANCEL", "ยกเลิก"}:
                conversation_state_service.clear_state(line_user_id)
                await line_service.reply_text_message(
                    reply_token,
                    "ยกเลิกการทำรายการแล้ว",
                )
                continue

            # -----------------------------------------------------
            # 2.3 ถ้ารอเลขสัญญาอยู่ -> verify ก่อน แล้วค่อย map
            # -----------------------------------------------------
            if user_state == "WAITING_CONTRACT_NO":
                contract_no = text

                try:
                    verify_result = await customer_service.verify_customer(
                        CustomerVerifyRequest(
                            contract_no=contract_no,
                            line_user_id=line_user_id,
                        )
                    )

                    if not verify_result.verified:
                        conversation_state_service.clear_state(line_user_id)
                        await line_service.reply_text_message(
                            reply_token,
                            (
                                "ไม่พบข้อมูลสัญญา\n"
                                f"เลขสัญญา: {contract_no}\n"
                                f"สาเหตุ: {verify_result.message}"
                            ),
                        )
                        continue

                    if not verify_result.eligible_to_map:
                        conversation_state_service.clear_state(line_user_id)
                        await line_service.reply_text_message(
                            reply_token,
                            (
                                "ไม่สามารถ map สัญญาได้\n"
                                f"เลขสัญญา: {verify_result.contract_no}\n"
                                f"ลูกค้า: {verify_result.customer_name or '-'}\n"
                                f"สถานะสัญญา: {verify_result.contract_status or '-'}\n"
                                f"สาเหตุ: {verify_result.message}"
                            ),
                        )
                        continue

                    map_result = await customer_service.map_customer(
                        CustomerMapRequest(
                            contract_no=contract_no,
                            line_user_id=line_user_id,
                        )
                    )

                    await db.commit()
                    conversation_state_service.clear_state(line_user_id)

                    await line_service.reply_text_message(
                        reply_token,
                        (
                            "Map สัญญาสำเร็จ\n"
                            f"เลขสัญญา: {map_result.contract_no}\n"
                            f"ลูกค้า: {map_result.customer_name}"
                        ),
                    )

                except ValueError as exc:
                    await db.rollback()
                    conversation_state_service.clear_state(line_user_id)
                    await line_service.reply_text_message(
                        reply_token,
                        f"ไม่สามารถ map ได้: {str(exc)}",
                    )

                except Exception:
                    await db.rollback()
                    conversation_state_service.clear_state(line_user_id)
                    await line_service.reply_text_message(
                        reply_token,
                        "เกิดข้อผิดพลาดระหว่างการ map สัญญา กรุณาลองใหม่อีกครั้ง",
                    )

                continue

            # -----------------------------------------------------
            # 2.4 fallback
            # -----------------------------------------------------
            await line_service.reply_text_message(
                reply_token,
                "พิมพ์ MAP เพื่อเริ่มผูกสัญญากับ LINE OA",
            )
            continue

    return {"status": "ok"}


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
                            "label": "MAP สัญญา",
                            "data": "action=map_contract",
                            "displayText": "MAP สัญญา",
                        },
                        {
                            "type": "message",
                            "label": "MAP",
                            "text": "MAP",
                        },
                        {
                            "type": "message",
                            "label": "ยกเลิก",
                            "text": "ยกเลิก",
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