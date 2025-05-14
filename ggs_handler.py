import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# อ่าน .env ผ่าน bot.py ก่อนแล้ว
SHEET_NAME = os.getenv("SHEET_NAME", "bot")

# ตั้ง scope และเชื่อม Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# ถ้าเซ็ต env var GGS_CREDENTIALS_JSON_PATH ให้ใช้ค่านั้น
# ถ้าไม่ ก็ใช้ mount path ของ Render โดยตรง
creds_json = os.getenv(
    "GGS_CREDENTIALS_JSON_PATH",
    "/run/secrets/credentials.json"
)

# สร้าง credentials จากไฟล์
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
gc = gspread.authorize(creds)

sh = gc.open(SHEET_NAME)
sheet1 = sh.worksheet("ชีต1")
sheet2 = sh.worksheet("Event_hw")

# ฟังก์ชันช่วยหา row ของ user
def find_user_row(username: str) -> int | None:
    users = sheet1.col_values(1)
    for i, name in enumerate(users, start=1):
        if name.strip().lower() == username.strip().lower():
            return i
    return None

# ฟังก์ชันอัปเดตคะแนนและบันทึกข้อความ
def record_submission(username: str, content: str) -> int:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = find_user_row(username)
    if not row:
        return -1

    current = int(sheet1.cell(row, 2).value or 0)
    new_score = current + 1
    sheet1.update_cell(row, 2, new_score)
    sheet2.append_row([username, content, now])
    return new_score
