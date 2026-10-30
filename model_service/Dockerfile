FROM python:3.13-slim

WORKDIR /credit-decisioning-service

RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY model_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ml/__init__.py ml/features.py ml/
COPY model_service/ model_service/

COPY artifacts/ artifacts/

EXPOSE 8000

CMD ["uvicorn", "model_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
