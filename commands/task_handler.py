import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, time
from ggs_handler import (
    record_task,
    update_user_exp,
    get_all_users,
    get_weekly_xp,
    XP_PER_REVIEW,
)

class TaskHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Forum parent channel IDs (comma-separated in ENV)
        ids = os.getenv("TASK_CHANNEL_IDS", "")
        self.task_channel_ids = [int(x) for x in ids.split(",") if x]
        self.noti_channel_id = int(os.getenv("NOTI_CHANNEL_ID", "0"))
        self.leaderboard_channel_id = int(os.getenv("LEADERBOARD_CHANNEL_ID", "0"))

        self.processed_threads = set()
        self.level_up_events = []
        # Start the weekly leaderboard task
        self.weekly_leaderboard_loop.start()

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        # Only respond in specified task channels
        if thread.parent_id not in self.task_channel_ids:
            return
        if thread.id in self.processed_threads:
            return

        # Fetch the opening message
        try:
            first_msg = await thread.fetch_message(thread.id)
        except discord.NotFound:
            return

        title = thread.name
        content = first_msg.content
        author = str(first_msg.author)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Record to Google Sheets
        record_task(title, content, author, timestamp)

        # Update XP and Level
        new_xp, new_level, leveled = update_user_exp(author)
        if leveled:
            self.level_up_events.append((author, new_level, timestamp))
            ch = self.bot.get_channel(self.noti_channel_id)
            if ch:
                await ch.send(
                    f":tada: {author} เลื่อนเป็น Level {new_level} แล้ว! 🎉"
                )

        self.processed_threads.add(thread.id)

    @commands.command(name="noti_lv_up")
    async def noti_lv_up(self, ctx: commands.Context):
        """แสดงการเลื่อน Level ล่าสุด และล้างรายการ"""
        if not self.level_up_events:
            await ctx.send("ยังไม่มีการเลื่อน Level ใหม่")
            return

        messages = [f"{u} -> Level {lvl} at {ts}" for u, lvl, ts in self.level_up_events]
        await ctx.send("\n".join(messages))
        self.level_up_events.clear()

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx: commands.Context):
        """แสดง Top10 Leaderboard ทั้ง Total และ Weekly พร้อมอันดับของคุณ"""
        # Total leaderboard
        users = get_all_users()
        total_sorted = sorted(users.items(), key=lambda x: x[1]['xp'], reverse=True)
        top_total = [f"{i+1}. {u} - {d['xp']} XP (Lv {d['level']})"
                     for i, (u, d) in enumerate(total_sorted[:10])]

        # Weekly leaderboard
        weekly = get_weekly_xp()
        weekly_sorted = sorted(weekly.items(), key=lambda x: x[1], reverse=True)
        top_week = [f"{i+1}. {u} - {xp} XP"
                    for i, (u, xp) in enumerate(weekly_sorted[:10])]

        # Find user's ranks
        author = str(ctx.author)
        ranks_total = [u for u, _ in total_sorted]
        if author in ranks_total:
            rank_total = ranks_total.index(author) + 1
            info = users[author]
            user_line = (
                f"Your Rank Total: {rank_total}. {author} - {info['xp']} XP (Lv {info['level']})"
            )
        else:
            user_line = "คุณยังไม่มีข้อมูลใน Leaderboard"

        if author in weekly:
            rank_week = [u for u, _ in weekly_sorted].index(author) + 1
            user_line += (
                f"\nYour Rank Weekly: {rank_week}. {author} - {weekly[author]} XP"
            )

        output = (
            "**📊 Leaderboard**\n"
            "**Total Top10**\n" + "\n".join(top_total) + "\n\n"
            "**Weekly Top10**\n" + "\n".join(top_week) + "\n\n"
            + user_line
        )
        await ctx.send(output)

    @tasks.loop(time=time(hour=0, minute=0))  # ทุกคืนวันเสาร์ เวลา UTC
    async def weekly_leaderboard_loop(self):
        users = get_all_users()
        total_sorted = sorted(users.items(), key=lambda x: x[1]['xp'], reverse=True)
        weekly = get_weekly_xp()
        weekly_sorted = sorted(weekly.items(), key=lambda x: x[1], reverse=True)

        embed = discord.Embed(
            title="📊 Weekly Leaderboard", timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="Total Top10",
            value="\n".join(
                [f"{i+1}. {u} - {d['xp']} XP (Lv {d['level']})"
                 for i, (u, d) in enumerate(total_sorted[:10])]
            ) or "ไม่มีข้อมูล",
            inline=False,
        )
        embed.add_field(
            name="Weekly Top10",
            value="\n".join(
                [f"{i+1}. {u} - {xp} XP"
                 for i, (u, xp) in enumerate(weekly_sorted[:10])]
            ) or "ไม่มีข้อมูล",
            inline=False,
        )

        ch = self.bot.get_channel(self.leaderboard_channel_id)
        if ch:
            await ch.send(embed=embed)

    @weekly_leaderboard_loop.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(TaskHandler(bot))