# LINE Contract Inquiry API (FastAPI, OOP)

โปรเจกต์นี้เป็นตัวอย่าง backend สำหรับกรณีที่ **D365 เป็นผู้รับภาระหลัก** ในการ
- verify ลูกค้า
- map LINE User กับ contract
- query ข้อมูลสัญญา
- inquiry ยอดค่างวด/ค้างชำระ
- unmap LINE User
- ดู payment history

โดย **ไม่มีส่วน Inno map logic** และทำเป็น FastAPI แบบ OOP พร้อมใช้งานทั้ง
- localhost
- Docker / Docker Compose

## Features
- FastAPI + Swagger
- SQLAlchemy Async + SQLite
- OOP structure: repository / service / endpoint
- seed data อัตโนมัติสำหรับ dev
- พร้อมทดสอบผ่าน `/docs`

## Project structure

```text
app/
  api/v1/endpoints/
  core/
  db/
  models/
  repositories/
  schemas/
  services/
  main.py
scripts/
  run_local.sh
  run_local.ps1
```

## APIs
- `POST /api/v1/customers/verify`
- `POST /api/v1/line-mappings`
- `GET /api/v1/contracts/by-line/{line_user_id}`
- `GET /api/v1/payments/inquiry/by-line/{line_user_id}`
- `POST /api/v1/line-mappings/unmap`
- `GET /api/v1/payments/history/by-line/{line_user_id}`
- `GET /health`

## Run on localhost

### 1) Create virtual environment

#### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open:
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Run with Docker Compose
```bash
docker compose up --build
```

Open:
- Swagger: `http://localhost:8000/docs`

## Sample flow

### 1) Verify customer
```json
{
  "contract_no": "EV0001",
  "id_card_no": "1103700000011",
  "mobile_no": "0811111111"
}
```

### 2) Map LINE User
```json
{
  "contract_no": "EV0001",
  "line_user_id": "U1234567890",
  "line_display_name": "Alisa Line"
}
```

### 3) Get contract by LINE
`GET /api/v1/contracts/by-line/U1234567890`

### 4) Get payment inquiry by LINE
`GET /api/v1/payments/inquiry/by-line/U1234567890`

## Seed data
โปรเจกต์นี้ seed ข้อมูลตัวอย่างให้อัตโนมัติเมื่อฐานข้อมูลว่าง
- Contracts: EV0001, EV0002, EV0003
- Payment schedules และ payment history

## Notes
- ใช้ SQLite เพื่อให้ทดสอบง่าย
- หากต้องการย้ายไป SQL Server หรือ PostgreSQL ให้เปลี่ยน `DATABASE_URL`
- โค้ดนี้เป็นจุดเริ่มต้นสำหรับ dev / SIT / API design ต่อกับ D365 ได้
