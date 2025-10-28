# --- Builder Stage ---
# Use python:3.11-slim for a smaller base image
FROM python:3.11-slim AS builder

# FIX: Moved to a single line to prevent copy-paste/indentation errors
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Set environment variables for Python build
ENV PIP_NO_CACHE_DIR=1     PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /wheels

# Copy ONLY the runtime requirements (from the root)
COPY requirements.txt ./

# Build 'wheels' (cached packages)
RUN pip wheel --wheel-dir=/wheels -r requirements.txt


# --- Final Runtime Stage ---
FROM python:3.11-slim AS runtime

# FIX: Moved to a single line to prevent copy-paste/indentation errors
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libpq5 && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PIP_NO_CACHE_DIR=1     PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# Create a non-root user for security (SRE best practice)
RUN groupadd --system appgroup && useradd --system --gid appgroup --home /app_root --create-home appuser

WORKDIR /app_root

# Copy 'wheels' from the builder stage
COPY --from=builder /wheels /wheels

# Copy runtime requirements
COPY requirements.txt /app_root/

# Install dependencies from local 'wheels' (fast and offline)
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Copy only the 'app' directory (our source code)
# This copies ./app into /app_root/app
COPY app/ /app_root/app/

# Grant ownership to the non-root user
RUN chown -R appuser:appgroup /app_root

USER appuser

# Expose the application port
EXPOSE 8000

# Command to run the application (referencing app/main.py)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
