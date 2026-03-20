import base64
import hashlib
import hmac
from datetime import date
from urllib.parse import parse_qs

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.repositories.contract_repository import ContractRepository
from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService


class LineMessagingService:
    def __init__(self) -> None:
        self.channel_access_token = settings.line_channel_access_token
        self.channel_secret = settings.line_channel_secret
        self.base_url = "https://api.line.me/v2/bot/message"

        if not self.channel_access_token:
            raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN is not configured.")
        if not self.channel_secret:
            raise RuntimeError("LINE_CHANNEL_SECRET is not configured.")

    def verify_signature(self, body: bytes, signature: str | None) -> bool:
        if not signature:
            return False

        digest = hmac.new(
            self.channel_secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).digest()

        expected_signature = base64.b64encode(digest).decode("utf-8")
        return hmac.compare_digest(expected_signature, signature)

    async def _post(self, path: str, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/{path}",
                headers=headers,
                json=payload,
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "message": "LINE Messaging API request failed.",
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        if not response.text:
            return {"ok": True}

        return response.json()

    async def reply_messages(self, reply_token: str, messages: list[dict]) -> dict:
        payload = {
            "replyToken": reply_token,
            "messages": messages,
        }
        return await self._post("reply", payload)

    async def push_messages(self, line_user_id: str, messages: list[dict]) -> dict:
        payload = {
            "to": line_user_id,
            "messages": messages,
        }
        return await self._post("push", payload)

    async def reply_text(self, reply_token: str, text: str) -> dict:
        return await self.reply_messages(
            reply_token,
            [{"type": "text", "text": text}],
        )

    async def push_text(self, line_user_id: str, text: str) -> dict:
        return await self.push_messages(
            line_user_id,
            [{"type": "text", "text": text}],
        )

    async def reply_main_menu(self, reply_token: str) -> dict:
        return await self.reply_messages(
            reply_token,
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

    def _format_payment_text(self, payment) -> str:
        return (
            "แจ้งยอดชำระ\n"
            f"สัญญา: {payment.contract_no}\n"
            f"งวดที่: {payment.billing_seq}\n"
            f"วันที่เรียกเก็บ: {payment.billing_date}\n"
            f"ยอดเรียกเก็บ: {payment.daily_rent_amount} บาท\n"
            f"ชำระแล้ว: {payment.paid_amount} บาท\n"
            f"คงค้าง: {payment.outstanding_amount} บาท\n"
            f"สถานะ: {payment.payment_status}"
        )

    def _parse_billing_date_from_text(self, text: str) -> date:
        """
        รองรับ:
        - ยอด
        - ยอด 2026-03-19
        """
        parts = text.strip().split()

        if len(parts) == 1:
            return date.today()

        if len(parts) >= 2:
            try:
                return date.fromisoformat(parts[1].strip())
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="รูปแบบวันที่ไม่ถูกต้อง กรุณาใช้ YYYY-MM-DD เช่น ยอด 2026-03-19",
                ) from exc

        return date.today()

    def _parse_billing_date_from_postback(self, data: str) -> date:
        parsed = parse_qs(data)
        billing_date_raw = parsed.get("billing_date", [None])[0]
        if not billing_date_raw:
            return date.today()

        try:
            return date.fromisoformat(billing_date_raw)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid billing_date in postback data.",
            ) from exc

    async def _reply_payment_inquiry(
        self,
        reply_token: str,
        line_user_id: str,
        billing_date: date,
        contract_repo: ContractRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        payment_service = PaymentService(contract_repo, payment_repo)

        payment = await payment_service.get_payment_inquiry_by_line_user_id(
            line_user_id=line_user_id,
            billing_date=billing_date,
        )

        text = self._format_payment_text(payment)
        await self.reply_text(reply_token, text)

    async def handle_follow_event(
        self,
        reply_token: str,
        line_user_id: str,
    ) -> None:
        message = (
            "ยินดีต้อนรับสู่ LINE Contract API\n"
            f"LINE User ID ของคุณคือ:\n{line_user_id}\n\n"
            "คำสั่งทดสอบ:\n"
            "- ping\n"
            "- help\n"
            "- ยอด\n"
            "- ยอด 2026-03-19\n"
            "- เมนู"
        )
        await self.reply_text(reply_token, message)

    async def handle_message_event(
        self,
        event: dict,
        contract_repo: ContractRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        reply_token = event["replyToken"]
        source = event.get("source", {})
        line_user_id = source.get("userId")
        message = event.get("message", {})
        text = (message.get("text") or "").strip()

        if not line_user_id:
            await self.reply_text(reply_token, "ไม่พบ LINE userId จาก event นี้")
            return

        if not text:
            await self.reply_text(reply_token, "รองรับเฉพาะข้อความตัวอักษรสำหรับการทดสอบนี้")
            return

        normalized = text.lower()

        if normalized == "ping":
            await self.reply_text(reply_token, "pong")
            return

        if normalized in {"help", "menu", "เมนู"}:
            await self.reply_main_menu(reply_token)
            return

        if text.startswith("ยอด"):
            billing_date = self._parse_billing_date_from_text(text)
            await self._reply_payment_inquiry(
                reply_token=reply_token,
                line_user_id=line_user_id,
                billing_date=billing_date,
                contract_repo=contract_repo,
                payment_repo=payment_repo,
            )
            return

        await self.reply_text(
            reply_token,
            (
                "ไม่เข้าใจคำสั่ง\n"
                "ลองใช้:\n"
                "- ping\n"
                "- help\n"
                "- เมนู\n"
                "- ยอด\n"
                "- ยอด 2026-03-19"
            ),
        )

    async def handle_postback_event(
        self,
        event: dict,
        contract_repo: ContractRepository,
        payment_repo: PaymentRepository,
    ) -> None:
        reply_token = event["replyToken"]
        source = event.get("source", {})
        line_user_id = source.get("userId")
        postback = event.get("postback", {})
        data = postback.get("data", "")

        if not line_user_id:
            await self.reply_text(reply_token, "ไม่พบ LINE userId จาก postback event")
            return

        parsed = parse_qs(data)
        action = parsed.get("action", [""])[0]

        if action == "payment_inquiry_today":
            billing_date = date.today()
            await self._reply_payment_inquiry(
                reply_token=reply_token,
                line_user_id=line_user_id,
                billing_date=billing_date,
                contract_repo=contract_repo,
                payment_repo=payment_repo,
            )
            return

        if action == "payment_inquiry":
            billing_date = self._parse_billing_date_from_postback(data)
            await self._reply_payment_inquiry(
                reply_token=reply_token,
                line_user_id=line_user_id,
                billing_date=billing_date,
                contract_repo=contract_repo,
                payment_repo=payment_repo,
            )
            return

        await self.reply_text(reply_token, f"Unknown postback action: {action}")
    
    def verify_signature(self, raw_body: bytes, x_line_signature: str | None) -> bool:
        if not x_line_signature:
            return False

        hash_value = hmac.new(
            self.channel_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).digest()
        computed_signature = base64.b64encode(hash_value).decode("utf-8")
        return hmac.compare_digest(computed_signature, x_line_signature)

    async def reply_text_message(self, reply_token: str, text: str) -> dict:
        url = "https://api.line.me/v2/bot/message/reply"
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": text,
                }
            ],
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json() if response.content else {}