# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any needed for pandas/numpy/etc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the dependency definition first to leverage Docker cache
COPY pyproject.toml .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install .

# Copy the rest of the application code
COPY . .

# Create directory for logs if it doesn't exist
RUN mkdir -p logs

# Default command to run the help menu
ENTRYPOINT ["python", "src/main.py"]
CMD ["--help"]
