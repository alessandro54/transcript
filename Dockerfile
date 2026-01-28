# ============================================
# Base stage with system dependencies
# ============================================
FROM python:3.13-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash botuser

# ============================================
# Builder stage for dependencies
# ============================================
FROM base AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Production stage
# ============================================
FROM base AS production

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=botuser:botuser . .

# Switch to non-root user
USER botuser

# Environment defaults for production
ENV ENVIRONMENT=production \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import transcript_bot" || exit 1

# Run the bot
CMD ["python", "run.py", "run"]

# ============================================
# Development stage
# ============================================
FROM base AS development

# Install dev dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=botuser:botuser . .

# Switch to non-root user
USER botuser

# Environment defaults for development
ENV ENVIRONMENT=development \
    PYTHONUNBUFFERED=1 \
    WHISPER_MODEL=base \
    WHISPER_DEVICE=cpu

# Run the bot
CMD ["python", "run.py", "run"]
