# Simple single-service Dockerfile for Render deployment
FROM node:18-alpine as frontend-build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build
# Verify the build output exists
RUN ls -la dist/

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend build output and verify
COPY --from=frontend-build /app/dist ./dist
RUN ls -la dist/

# Expose port for Render
EXPOSE 10000

# Set environment variables
ENV PORT=10000
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]