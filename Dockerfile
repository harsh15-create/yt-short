FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Expose port required by Render/Railway
EXPOSE 8080

# Start server
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "--timeout", "300", "server:app"]
