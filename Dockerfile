FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data/commercial_catalog.json ./data/commercial_catalog.json

RUN python -m pip install --upgrade pip && \
    pip install .

RUN mkdir -p /app/data

EXPOSE 8765

CMD ["uvicorn", "hakham.web_latest:app", "--host", "0.0.0.0", "--port", "8765"]
