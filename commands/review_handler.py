import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from ggs_handler import record_review, record_comment, update_user_exp, XP_PER_REVIEW

class ReviewHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.REVIEW_CHANNEL_ID = int(os.getenv("REVIEW_CHANNEL_ID"))
        # เก็บว่าคอมเมนต์ของ user ในแต่ละ thread ถูกนับแล้วหรือยัง
        self.processed_comments: dict[int, set[int]] = {}
        # ช่วยป้องกันสแปม แต่ละ user ต่อ thread ครั้งเดียว
        self.spam_protect: dict[tuple[int,int], datetime] = {}

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        # บันทึก intro แบบเดิม (รันครั้งเดียวตอนสร้าง)
        if thread.parent_id != self.REVIEW_CHANNEL_ID:
            return
        # ... (โค้ดเดิมของ on_thread_create) ...

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # แยกเฉพาะข้อความใน Thread ของ Review Channel
        if message.author.bot:
            return
        ch = message.channel
        if not (isinstance(ch, discord.Thread) and ch.parent_id == self.REVIEW_CHANNEL_ID):
            return
        # ข้ามข้อความ starter (id เท่ากับ thread id)
        if message.id == ch.id:
            return

        user_id = message.author.id
        thread_id = ch.id
        key = (thread_id, user_id)
        now = datetime.utcnow()
        # spam protection 60 วิ
        last = self.spam_protect.get(key)
        if last and (now - last) < timedelta(seconds=60):
            return
        self.spam_protect[key] = now

        # ถ้ายังไม่เคยนับคอมเมนต์ของ user นี้ใน thread นี้
        if thread_id not in self.processed_comments:
            self.processed_comments[thread_id] = set()
        if user_id in self.processed_comments[thread_id]:
            return

        # บันทึกคอมเมนต์ลง Google Sheets
        title     = ch.name
        content   = message.content
        author    = str(message.author)
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        record_comment(title, content, author, timestamp)

        # อัปเดต XP และ Level
        new_xp, new_level, leveled_up = update_user_exp(author)
        self.processed_comments[thread_id].add(user_id)

        # ตอบกลับใน thread
        reply = (
            f"{message.author.mention} ✅ คุณได้รับ {XP_PER_REVIEW} XP (รวม {new_xp} XP), Level: {new_level}"
        )
        if leveled_up:
            reply += f" 🎉 ยินดีด้วย! เลื่อนเป็น Level {new_level} แล้ว"
        await ch.send(reply)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReviewHandler(bot))