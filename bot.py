import discord
from discord.ext import commands, tasks
import requests
import os

# Load secrets from environment
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
UPTIMEROBOT_API_KEY = os.getenv("UPTIMEROBOT_API_KEY")

# Bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_uptime.start()  # Start scheduled task

@tasks.loop(minutes=5)
async def check_uptime():
    monitor_data = get_monitor_data()
    if monitor_data:
        for monitor in monitor_data:
            name = monitor["friendly_name"]
            status = monitor["status"]
            status_text = {
                2: "🟢 UP",
                9: "🔴 DOWN",
                1: "⏸️ PAUSED"
            }.get(status, "❓ Unknown")

            print(f"[Status Check] {name}: {status_text}")

            # Optionally update bot's status with first monitor
            await bot.change_presence(activity=discord.Game(name=f"{name} is {status_text}"))
            break  # Only use the first monitor for status

@bot.command()
async def status(ctx):
    monitor_data = get_monitor_data()
    if monitor_data:
        embed = discord.Embed(title="📡 Uptime Monitor Status", color=0x00ff00)
        for monitor in monitor_data:
            name = monitor["friendly_name"]
            url = monitor["url"]
            status = monitor["status"]
            status_text = {
                2: "🟢 UP",
                9: "🔴 DOWN",
                1: "⏸️ PAUSED"
            }.get(status, "❓ Unknown")
            embed.add_field(name=name, value=f"{status_text}\n{url}", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("⚠️ Couldn't fetch monitor status.")

def get_monitor_data():
    try:
        url = "https://api.uptimerobot.com/v2/getMonitors"
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "api_key": UPTIMEROBOT_API_KEY,
            "format": "json"
        }

        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            monitors = response.json().get("monitors", [])
            return monitors
        else:
            print("❌ API Error:", response.status_code, response.text)
            return None
    except Exception as e:
        print("❌ Exception:", e)
        return None

# Start bot
bot.run(DISCORD_TOKEN)
