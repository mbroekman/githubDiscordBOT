FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (specifically for the "Upload File" functionality)
RUN apt-get update && apt-get install -y \
    curl \
    libcurl4-openssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "githubBOT.py"]