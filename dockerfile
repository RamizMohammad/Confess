# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements (cached layer)
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

# Copy application code
COPY server/ server/
COPY templates/ templates/
COPY static/ static/

# Expose the port FastAPI will run on
EXPOSE 8080

# Set entrypoint to run the app using uvicorn
CMD ["uvicorn", "server.Routes:app", "--host", "0.0.0.0", "--port", "8080"]
