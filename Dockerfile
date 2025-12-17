FROM python:3.9-slim

# Install system dependencies (ffmpeg is required for audio conversion)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Default port environment variable
ENV PORT=8080

# Expose port 8080 (documentation only, actual binding depends on CMD)
EXPOSE 8080

# Run the application with Gunicorn, binding to the PORT environment variable
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 server:app
