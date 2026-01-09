# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY orc/requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy the ORC package
COPY orc/ ./orc/
COPY setup.py .

# Install ORC
RUN pip install -e .

# Create non-root user
RUN adduser --disabled-password --gecos '' orcuser \
    && chown -R orcuser:orcuser /app
USER orcuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "orc.web.app_prod:app"]