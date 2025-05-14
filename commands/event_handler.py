import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from ggs_handler import record_submission

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_users: dict[str, datetime] = {}
        self.TARGET_PARENT_ID = int(os.getenv("TARGET_PARENT_ID"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        ch = message.channel
        is_main = (ch.id == self.TARGET_PARENT_ID)
        is_thread = isinstance(ch, discord.Thread) and (ch.parent_id == self.TARGET_PARENT_ID)
        if not (is_main or is_thread):
            return

        if isinstance(ch, discord.Thread) and ch.parent_id == self.TARGET_PARENT_ID:
            user = str(message.author)
            now = datetime.now()
            last = self.recent_users.get(user)
            if last and (now - last) < timedelta(seconds=60):
                return
            self.recent_users[user] = now

            new_score = record_submission(user, message.content)
            if new_score < 0:
                await message.channel.send(f"{message.author.mention} ❌ ยังไม่มีชื่อในระบบ กรุณาติดต่อผู้ดูแล")
            else:
                await message.channel.send(f"{message.author.mention} ✅ ส่งงานสำเร็จ! คะแนนรวม: {new_score}")

# ฟังก์ชัน setup ต้องเป็น async def เพื่อให้ load_extension สามารถ await ได้
async def setup(bot: commands.Bot):
    await bot.add_cog(EventHandler(bot))
