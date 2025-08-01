FROM python:3.9-slim

WORKDIR /app

COPY src/core /app/core
COPY src/document_processing /app/document_processing
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["uvicorn", "document_processing.api:app", "--host", "0.0.0.0", "--port", "8001"]
