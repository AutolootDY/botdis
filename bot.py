import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.messages = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.commands_path = os.path.join(os.path.dirname(__file__), "commands")

    async def setup_hook(self):
        for filename in os.listdir(self.commands_path):
            # ข้าม __init__.py
            if not filename.endswith(".py") or filename == "__init__.py":
                continue
            ext = f"commands.{filename[:-3]}"
            try:
                await self.load_extension(ext)
                print(f"✅ Loaded {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}: {e}")

    # async def on_ready(self):
    #     print(f"✅ Bot พร้อมใช้งาน: {self.user}")
    async def on_ready(self):
        print(f"✅ Bot พร้อมใช้งาน: {self.user}", flush=True)


bot = MyBot()
bot.run(TOKEN)
