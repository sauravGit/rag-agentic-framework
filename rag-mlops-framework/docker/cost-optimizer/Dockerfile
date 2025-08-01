FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/cost_optimization /app/cost_optimization
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8004

CMD ["uvicorn", "cost_optimization.api:app", "--host", "0.0.0.0", "--port", "8004"]
