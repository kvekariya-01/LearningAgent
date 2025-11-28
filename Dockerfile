# Dockerfile for Learning Agent API - Hugging Face Spaces
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=5000
ENV USE_IN_MEMORY_DB=true
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]