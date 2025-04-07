import aiosqlite

async def check_tables():
    async with aiosqlite.connect("messages.db") as conn:
        cursor = await conn.cursor()
        await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = await cursor.fetchall()
        print("Таблицы в базе данных:", tables)

asyncio.run(check_tables())