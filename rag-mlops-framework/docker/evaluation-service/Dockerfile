FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/evaluation /app/evaluation
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003

CMD ["uvicorn", "evaluation.api:app", "--host", "0.0.0.0", "--port", "8003"]
