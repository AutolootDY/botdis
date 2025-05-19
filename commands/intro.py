# import os
# import discord
# from discord.ext import commands
# from ggs_handler import record_intro

# class IntroHandler(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         # ID ของ Forum Channel แนะนำตัว (จาก ENV)
#         self.FORUM_CHANNEL_ID = int(os.getenv("INTRO_FORUM_CHANNEL"))

#     @commands.Cog.listener()
#     async def on_thread_create(self, thread: discord.Thread):
#         """
#         เมื่อสร้าง thread ใหม่ใน Forum Channel ที่กำหนด
#         ให้ดึง title, tags, เนื้อหาแรก, ผู้เขียน มา record_intro
#         """
#         # ตรวจว่าเป็น thread ภายใต้ Forum Channel ของเรา
#         if thread.parent_id != self.FORUM_CHANNEL_ID:
#             return

#         # ดึงข้อความแรก (starter message ของ thread)
#         try:
#             first_msg = await thread.fetch_message(thread.id)
#         except discord.NotFound:
#             return

#         title = thread.name
#         tags = [tag.name for tag in thread.applied_tags]
#         content = first_msg.content
#         author  = str(first_msg.author)

#         # บันทึกลง Google Sheets
#         record_intro(title, tags, content, author)

#         # ส่งข้อความยืนยันกลับใน thread (ถ้าต้องการ)
#         try:
#             await thread.send("✅ บันทึก ลง Google Sheets เรียบร้อยแล้ว!")
#         except:
#             pass

# async def setup(bot: commands.Bot):
#     await bot.add_cog(IntroHandler(bot))

# commands/intro_handler.py

import os
import discord
from discord.ext import commands
from ggs_handler import record_intro

class IntroHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # ID ของ Forum Channel แนะนำตัว (จาก ENV)
        self.FORUM_CHANNEL_ID = int(os.getenv("INTRO_FORUM_CHANNEL"))
        # เก็บ thread.id ที่เคยบันทึกแล้ว
        self.processed_threads: set[int] = set()

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        """
        เมื่อสร้าง thread ใหม่ใน Forum Channel ที่กำหนด
        จะบันทึก intro รอบเดียว แล้วเก็บ thread.id
        """
        # ข้ามถ้าไม่ใช่ thread ใต้ Forum Channel นั้น
        if thread.parent_id != self.FORUM_CHANNEL_ID:
            return

        # ถ้าเคยบันทึก thread นี้แล้ว ก็ข้าม
        if thread.id in self.processed_threads:
            return

        # ดึงข้อความแรกเป็น intro
        try:
            first_msg = await thread.fetch_message(thread.id)
        except discord.NotFound:
            return

        title   = thread.name
        tags    = [tag.name for tag in thread.applied_tags]
        content = first_msg.content
        author  = str(first_msg.author)

        # บันทึกลง Google Sheets
        record_intro(title, tags, content, author)

        # เพิ่มใน set เพื่อไม่ให้บันทึกซ้ำ
        self.processed_threads.add(thread.id)

        # ตอบกลับใน thread แค่ครั้งแรก
        await thread.send("✅ บันทึก intro ลง Google Sheets เรียบร้อยแล้ว!")

async def setup(bot: commands.Bot):
    await bot.add_cog(IntroHandler(bot))

###แก้ปัญหานี้ ระบบจะบันทึกข้อมูล intro ให้แค่รอบเดียวต่อการสร้างโพสต์ครับ! จะไม่บันทึกซ้ำ เวลามีคนซ้ำโพสต์