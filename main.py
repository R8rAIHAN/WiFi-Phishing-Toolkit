import asyncio
import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from bot import bot, dp, init_db
from web import router as web_router

load_dotenv()

async def main():
    await init_db()
    print("✅ PostgreSQL Connected & Tables Created!")
    
    asyncio.create_task(dp.start_polling(bot))
    
    config = uvicorn.Config("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

app = FastAPI(title="Phishing Dashboard")
app.include_router(web_router)

if __name__ == "__main__":
    asyncio.run(main())
