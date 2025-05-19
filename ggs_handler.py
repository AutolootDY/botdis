# import os
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from datetime import datetime
# import json    

# # อ่าน .env ผ่าน bot.py ก่อนแล้ว
# SHEET_NAME = os.getenv("SHEET_NAME", "bot")

# # ตั้ง scope และเชื่อม Google Sheets
# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive"
# ]

# # ถ้าเซ็ต env var GGS_CREDENTIALS_JSON_PATH ให้ใช้ค่านั้น
# # ถ้าไม่ ก็ใช้ mount path ของ Render โดยตรง
# # creds_json = os.getenv(
# #     "GGS_CREDENTIALS_JSON_PATH",
# #     "/run/secrets/credentials.json"
# # )

# # print("🔍 Secrets dir:", os.listdir("/run/secrets"), flush=True)

# # creds_json = ServiceAccountCredentials.from_json_keyfile_name(
# #     "/run/secrets/credentials.json", scope
# # )
# creds_json = json.loads(os.getenv("GGS_CREDENTIALS_JSON"))
# # สร้าง credentials จากไฟล์
# creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
# gc = gspread.authorize(creds)

# sh = gc.open(SHEET_NAME)
# sheet1 = sh.worksheet("ชีต1")
# sheet2 = sh.worksheet("Event_hw")

# # ฟังก์ชันช่วยหา row ของ user
# def find_user_row(username: str) -> int | None:
#     users = sheet1.col_values(1)
#     for i, name in enumerate(users, start=1):
#         if name.strip().lower() == username.strip().lower():
#             return i
#     return None

# # ฟังก์ชันอัปเดตคะแนนและบันทึกข้อความ
# def record_submission(username: str, content: str) -> int:
#     now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
#     row = find_user_row(username)
#     if not row:
#         return -1

#     current = int(sheet1.cell(row, 2).value or 0)
#     new_score = current + 1
#     sheet1.update_cell(row, 2, new_score)
#     sheet2.append_row([username, content, now])
#     return new_score
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime ,timedelta

# อ่าน .env ผ่าน bot.py ก่อนแล้ว
SHEET_NAME = os.getenv("SHEET_NAME", "bot")

# ตั้ง scope และเชื่อม Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
# credentials.json จะถูกเขียนก่อนรัน (บน Render หรือ local)
creds_json = os.getenv("GGS_CREDENTIALS_JSON_PATH", "credentials.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
gc = gspread.authorize(creds)

sh = gc.open(SHEET_NAME)
sheet1 = sh.worksheet("ชีต1")
sheet2 = sh.worksheet("Event_hw")

# Constants สำหรับการคำนวณ XP/Level
XP_PER_REVIEW = 1         # ปรับได้ตามต้องการ
COEFFICIENT = 1           # ค่า a ในสูตร xp_req = a * level^2



# ฟังก์ชันช่วยหา row ของ user
def find_user_row(username: str) -> int | None:
    users = sheet1.col_values(1)
    for i, name in enumerate(users, start=1):
        if name.strip().lower() == username.strip().lower():
            return i
    return None

# ฟังก์ชันอัปเดตคะแนนและบันทึกข้อความ
def record_submission(username: str, content: str) -> int:
    now = datetime.utcnow()+ + timedelta(hours=7)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    row = find_user_row(username)
    if not row:
        return -1

    current = int(sheet1.cell(row, 2).value or 0)
    new_score = current + 1
    sheet1.update_cell(row, 2, new_score)
    sheet2.append_row([username, content, timestamp])
    return new_score


def record_intro(title: str, tags: list[str], content: str, author: str) -> None:
    """
    บันทึกข้อมูลห้องแนะนำตัว:
    Title | Tags | Author | Content | Timestamp
    ลงชีตชื่อ "Intro"
    """
    sheet_intro = sh.worksheet("Auto_record_text_in_forum_to_ggs")  # ต้องสร้างชีตชื่อ Intro ไว้ก่อน
    now = datetime.utcnow() + timedelta(hours=7)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    tag_str = ",".join(tags)
    sheet_intro.append_row([title, tag_str, author, content, timestamp])

# def record_homework(title: str, content: str, author: str, timestamp: str) -> int | None:
#     """
#     บันทึก Title | Author | Content | Timestamp ลงชีต "Homework"
#     คืนคะแนนใหม่ (int) ถ้าบันทึกครั้งแรก, คืน None ถ้าเคยส่งแล้ว
#     """
#     sheet = sh.worksheet("Event_hw")  # ต้องสร้างชีตชื่อ Homework ไว้ก่อน
#     # ตรวจว่าผู้ใช้เคยส่งกระทู้นี้หรือยัง
#     for row in sheet.get_all_records():
#         if row["Title"] == title and row["Author"] == author:
#             return None

#     # ยังไม่เคยส่ง: บันทึกข้อมูลลงชีต
#     sheet.append_row([title, author, content, timestamp])

#     # เพิ่มคะแนนใน sheet1
#     rownum = find_user_row(author)
#     if rownum:
#         current = int(sheet1.cell(rownum, 2).value or 0)
#         new_score = current + 1
#         sheet1.update_cell(rownum, 2, new_score)
#         return new_score
#     return 0

def record_review(title: str, content: str, author: str, timestamp: str) -> None:
    """
    บันทึกข้อมูลกระทู้ทบทวนบทเรียน:
    Title | Content | Author | Timestamp
    ลงชีตชื่อ "Review"
    """
    sheet_rev = sh.worksheet("Event_score_active_chat_leveling")  # สร้างชีตชื่อ "Review" ไว้ก่อนใน Google Sheets
    sheet_rev.append_row([title, content, author, timestamp])

def record_comment(title: str, content: str, author: str, timestamp: str) -> None:
    """
    บันทึกข้อมูลการคอมเมนต์ทบทวนบทเรียน:
    Title | Content | Author | Timestamp
    ลงชีตชื่อ "Event_score_active_chat_leveling"
    """
    sheet_comments = sh.worksheet("Event_score_active_chat_leveling")  # สร้างชีตชื่อ "Event_score_active_chat_leveling" ใน Google Sheets
    sheet_comments.append_row([title, content, author, timestamp])

def update_user_exp(author: str) -> tuple[int, int, bool]:
    """
    เพิ่ม XP ให้ผู้ใช้โดยใช้ quadratic growth:
    - XP ใหม่ = XP เก่า + XP_PER_REVIEW
    - Level ใหม่ = floor(sqrt(XP ใหม่ / COEFFICIENT))
    คืนค่า (new_xp, new_level, leveled_up)
    """
    sheet_users = sh.worksheet("Users")  # สร้างชีตชื่อ "Users" ไว้ก่อน: Col1=User, Col2= , Col3=Level
    users = sheet_users.col_values(1)
    # หา row ของ user
    if author in users:
        row = users.index(author) + 1
        old_xp = int(sheet_users.cell(row, 2).value or 0)
        old_level = int(sheet_users.cell(row, 3).value or 0)
        new_xp = old_xp + XP_PER_REVIEW
        sheet_users.update_cell(row, 2, new_xp)
    else:
        # ถ้าไม่มี user ให้เพิ่มใหม่
        users_count = len(users)
        row = users_count + 1
        new_xp = XP_PER_REVIEW
        old_level = 0
        sheet_users.update_cell(row, 1, author)
        sheet_users.update_cell(row, 2, new_xp)
        sheet_users.update_cell(row, 3, 0)

    # คำนวณ level ใหม่
    new_level = int((new_xp / COEFFICIENT) ** 0.5)
    if new_level > old_level:
        sheet_users.update_cell(row, 3, new_level)
        leveled_up = True
    else:
        leveled_up = False

    return new_xp, new_level, leveled_up


###### active user ######
# บันทึก submission ในห้องต่างๆ
def record_task(title: str, content: str, author: str, timestamp: str) -> None:
    """
    บันทึกข้อมูล submission:
    Title | Content | Author | Timestamp
    ลงชีตชื่อ "Tasks"
    """
    sheet_tasks = sh.worksheet("Tasks")  # สร้างชีตชื่อ "Tasks"
    sheet_tasks.append_row([title, content, author, timestamp])

# ดึงข้อมูล Users ทั้งหมดจากชีต Users
# คืน dict: {username: {'xp': int, 'level': int}}
def get_all_users() -> dict[str, dict[str, int]]:
    sheet_users = sh.worksheet("Users")
    records = sheet_users.get_all_records()
    users = {}
    for r in records:
        name = r.get('User')
        xp   = int(r.get('XP', 0))
        lvl  = int(r.get('Level', 0))
        users[name] = {'xp': xp, 'level': lvl}
    return users

# คำนวณ XP ที่ได้ในช่วง 7 วันที่ผ่านมา จากชีต Tasks
# คืน dict: {username: xp_in_week}
def get_weekly_xp() -> dict[str, int]:
    sheet_tasks = sh.worksheet("Tasks")
    records = sheet_tasks.get_all_records()
    weekly = {}
    week_ago = datetime.utcnow() - timedelta(days=7)
    for r in records:
        ts = datetime.strptime(r.get('Timestamp'), "%Y-%m-%d %H:%M:%S")
        if ts >= week_ago:
            author = r.get('Author')
            weekly[author] = weekly.get(author, 0) + 1  # 1 XP per task
    return weekly
