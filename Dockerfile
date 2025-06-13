FROM python:3.13-slim

WORKDIR /app

# Install Rust, required build tools, pkg-config, and OpenSSL development libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    build-essential \
    pkg-config \
    libssl-dev \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
ENV PATH="/root/.cargo/bin:${PATH}"

COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE ${PORT:-8000}
CMD ["python", "main.py"]