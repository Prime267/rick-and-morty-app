# Multi-stage Dockerfile optimized for Python web apps using pip wheel

# --- Builder Stage ---
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Python build
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /wheels

# Copy dependency file
COPY requirements.txt ./

# Build wheels for dependencies
RUN pip wheel --wheel-dir=/wheels -r requirements.txt


# --- Final Runtime Stage ---
FROM python:3.11-slim AS runtime

# Install minimal runtime OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libpq5 \ 
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user and group for security
RUN groupadd --system appgroup && useradd --system --gid appgroup --home /app_root --create-home appuser

WORKDIR /app_root

# Copy built wheels from builder stage
COPY --from=builder /wheels /wheels
# Copy requirements file
COPY requirements.txt /app_root/

# Install dependencies from wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy only the app directory
COPY app/ /app_root/app/

# Change ownership to the non-root user
RUN chown -R appuser:appgroup /app_root

USER appuser

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]