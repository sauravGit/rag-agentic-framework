FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/monitoring /app/monitoring
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9090

CMD ["uvicorn", "monitoring.api:app", "--host", "0.0.0.0", "--port", "9090"]
