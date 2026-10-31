FROM python:3.11-slim

# Python settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        libpng-dev \
        libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project and set ownership
COPY . .
RUN chown -R app:app /code

USER app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]