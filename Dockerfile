# Use the Python image
ARG BASE_IMAGE=python:3.9-slim-buster
FROM $BASE_IMAGE

# Set the working directory to /app
WORKDIR /app

# system update & package install
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copied requirements.txt file to the current image directory
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
# requirements
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy all files from the current directory (where the Dockerfile is located) to /app in the image
COPY . .

# Execute
CMD ["python", "main.py"]