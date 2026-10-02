FROM python:3.11-slim

# Install system dependencies for manim (ffmpeg, cairo, pango) and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

# The web process does not need root privileges. A dedicated user limits the
# impact of a compromised dependency or malformed request.
RUN useradd --create-home --uid 10001 celestia \
    && chown -R celestia:celestia /app
USER celestia
ENV HOME=/home/celestia

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:' + __import__('os').environ.get('PORT', '8501') + '/_stcore/health', timeout=3)" || exit 1

# Render dynamically assigns a port to $PORT, otherwise default to 8501
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]
