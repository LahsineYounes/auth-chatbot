# Use the latest Python 3.11.x slim image for security patches
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies and update packages
RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y --no-install-recommends gcc python3-dev && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]