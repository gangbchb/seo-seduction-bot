import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect("messages.db")
c = conn.cursor()

# Считаем количество записей
c.execute("SELECT COUNT(*) FROM messages")
count = c.fetchone()[0]
print(f"Всего сообщений в базе: {count}")

# Выводим первые 5 записей
print("\nПервые 5 записей:")
c.execute("SELECT * FROM messages LIMIT 5")
for row in c.fetchall():
    print(row)

# Закрываем соединение
conn.close()