FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for Pillow/Reportlab (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --clear || echo "Warning: collectstatic skipped, continuing build..."

EXPOSE 8000

# Use Gunicorn for production instead of runserver
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "takecare.wsgi:application"]
