# Base image
FROM python:3.11-slim

# Set workdir inside container
WORKDIR /app

# Copy requirements from current directory first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to /app
COPY . .

# Create non-root user to match host UID/GID
ARG API_UID=1000
ARG API_GID=1000
RUN groupadd -g $API_GID apiuser \
    && useradd -m -u $API_UID -g apiuser apiuser \
    && chown -R apiuser:apiuser /app

USER apiuser

# Set environment variables
ENV DATA_PATH=/shared-data
ENV API_PORT=${API_PORT:-8005}

# Expose API port (will be set by build arg)
EXPOSE ${API_PORT:-8005}

# Run FastAPI - now main.py is at /app/app/main.py, so we use app.main:app
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8005}"