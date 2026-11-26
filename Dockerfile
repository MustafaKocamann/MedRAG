## Parent image (Local environment: Python 3.13)
FROM python:3.13-slim

## Essential environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

## Work directory inside the docker container
WORKDIR /app

## Installing system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy project configuration first for layer caching
COPY pyproject.toml README.md ./

## Install Python dependencies via pyproject.toml
RUN pip install --no-cache-dir .

## Copying remaining application contents
COPY . .

## Expose Flask port
EXPOSE 5000

## Run the Flask app
CMD ["python", "app/application.py"]
