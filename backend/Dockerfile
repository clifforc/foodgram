FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir

COPY data/ ../data
COPY backend/ .

CMD ["sh", "entrypoint.sh"]