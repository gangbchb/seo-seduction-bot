import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, PHONE, SESSION

async def main():
    app = Client(
        name=SESSION,
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE
    )
    await app.start()
    print("Сессия успешно создана! Теперь можешь запустить main.py.")
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())