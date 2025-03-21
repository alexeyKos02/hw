# Dockerfile
FROM python:3.13-slim

# Установка зависимостей для grpcio
RUN apt-get update && apt-get install -y build-essential libssl-dev libffi-dev python3-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]
