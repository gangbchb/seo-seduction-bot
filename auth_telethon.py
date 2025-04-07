import os
from telethon import TelegramClient

# Переменные окружения
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")

# Создай Telethon-клиент
client = TelegramClient('session', api_id, api_hash)

async def main():
    # Подключись
    await client.start(phone=phone)
    print("Авторизация завершена!")
    await client.disconnect()

# Запусти авторизацию
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())