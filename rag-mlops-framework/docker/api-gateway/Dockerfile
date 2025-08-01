FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/api_gateway /app/api_gateway
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
