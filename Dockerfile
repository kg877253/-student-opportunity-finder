FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir fastapi uvicorn pydantic

COPY . .

EXPOSE 7860

ENV PORT=7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]