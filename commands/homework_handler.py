# # commands/homework_handler.py

# import os
# import discord
# from discord.ext import commands
# from datetime import datetime
# from ggs_handler import record_homework  # ต้องเขียนฟังก์ชันนี้ใน ggs_handler.py

# class HomeworkHandler(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         # ID ของ Forum Channel ที่ใช้ส่งการบ้าน (ตั้งใน .env)
#         self.TARGET_PARENT_ID = int(os.getenv("HOMEWORK_FORUM_CHANNEL"))
#         # เก็บ set ของผู้ใช้ที่ส่งในแต่ละ thread เพื่อป้องกันส่งซ้ำ
#         # โครงสร้าง: { thread_id: set([username1, username2, ...]) }
#         self.submissions: dict[int, set[str]] = {}

#     @commands.Cog.listener()
#     async def on_message(self, message: discord.Message):
#         # ข้าม bot เอง
#         if message.author.bot:
#             return

#         ch = message.channel

#         # เช็คว่าเป็น Thread ภายใต้ Forum Channel ที่เรากำหนด
#         if not (isinstance(ch, discord.Thread) and ch.parent_id == self.TARGET_PARENT_ID):
#             return

#         thread_id = ch.id
#         user = str(message.author)

#         # ถ้ายังไม่มีการลงทะเบียน thread นี้ ให้สร้าง set ใหม่
#         if thread_id not in self.submissions:
#             self.submissions[thread_id] = set()

#         # ถ้าผู้ใช้นี้เคยส่งไปแล้ว ก็ไม่ให้คะแนนซ้ำ
#         if user in self.submissions[thread_id]:
#             return

#         # บันทึกข้อมูลส่งการบ้านและอัปเดตคะแนน
#         # record_homework คืนค่าเป็น None ถ้าเคยส่งแล้ว,
#         # หรือคืนคะแนนใหม่ (int) ถ้าบันทึกสำเร็จ
#         timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
#         new_score = record_homework(
#             title=ch.name,
#             content=message.content,
#             author=user,
#             timestamp=timestamp
#         )

#         # บันทึกแล้วก็เก็บ user นี้ไว้ใน set thread นี้
#         self.submissions[thread_id].add(user)

#         # ตอบกลับใน thread
#         if new_score is None:
#             await ch.send(f"{message.author.mention} ❌ คุณส่งการบ้านไปแล้วในกระทู้นี้")
#         else:
#             await ch.send(f"{message.author.mention} ✅ ส่งการบ้านเรียบร้อย! คะแนนรวม: {new_score}")

# # ต้องเป็น async setup เพื่อให้ load_extension await ได้
# async def setup(bot: commands.Bot):
#     await bot.add_cog(HomeworkHandler(bot))
