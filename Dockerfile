FROM python:3.9-slim

WORKDIR /app

# Сначала копируем только requirements.txt
COPY requirements.txt .

# Пробуем разные варианты установки
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 -r requirements.txt || \
    python -m pip install --no-cache-dir -r requirements.txt || \
    pip install --user --no-cache-dir -r requirements.txt

# Затем копируем остальные файлы
COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]