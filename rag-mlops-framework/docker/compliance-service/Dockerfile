FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/compliance /app/compliance
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8002

CMD ["uvicorn", "compliance.api:app", "--host", "0.0.0.0", "--port", "8002"]
