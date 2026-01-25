# Use an official Python slim image
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy project files
COPY app/ ./app/
COPY config.yml .
COPY .env.example .env

# Create directories for output and logs
RUN mkdir -p output/documents logs

# Create a non-root user and switch to it
RUN addgroup --system appgroup && adduser --system --group appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Expose port for health check
EXPOSE 5000

# Run the application
CMD ["python", "app/main.py"]
