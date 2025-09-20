FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Открываем порт
EXPOSE 8082

CMD ["python", "main.py"]
# DEBUG ONLY - Keep container alive without running app - just provide shell access
# CMD ["tail", "-f", "/dev/null"]