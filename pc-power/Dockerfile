FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for shutdown command
RUN apt-get update && apt-get install -y --no-install-recommends \
    util-linux \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Set environment variables
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5001
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/api/health', timeout=2)" || exit 1

# Run Flask app
CMD ["python", "src/flask_app.py"]
