FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/agent_orchestration /app/agent_orchestration
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "agent_orchestration.api:app", "--host", "0.0.0.0", "--port", "8000"]
