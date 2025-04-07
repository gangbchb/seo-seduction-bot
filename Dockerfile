# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем pip до последней версии
RUN pip install --upgrade pip --root-user-action=ignore

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

# Копируем остальные файлы проекта
COPY . .

# Загружаем данные NLTK во время сборки
RUN python download_nltk_data.py

# Устанавливаем переменную окружения для NLTK
ENV NLTK_DATA=/app/nltk_data

# Указываем команду для запуска приложения
CMD ["python", "main.py"]