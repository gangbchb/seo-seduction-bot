import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Очищаем таблицу messages
cursor.execute("DELETE FROM messages")
conn.commit()

# Закрываем соединение
conn.close()

print("Database cleared successfully.")