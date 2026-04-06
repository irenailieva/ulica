FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for Playwright and other basic tools
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browsers
RUN playwright install --with-deps chromium

COPY . .

# Command to run the scraper
CMD ["python", "scraper.py"]
