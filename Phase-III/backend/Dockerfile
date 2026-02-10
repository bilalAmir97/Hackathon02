# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv package manager
RUN pip install uv

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port (HF Spaces uses PORT env var, default to 7860)
EXPOSE 7860

# Start command - use PORT env var from HF Spaces
CMD uv run uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-7860}
