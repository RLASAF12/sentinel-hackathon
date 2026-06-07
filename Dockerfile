FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application.
COPY . .

ENV PORT=8080
EXPOSE 8080

# Cloud Run sends traffic to $PORT. Serve the web UI (the risk-gate centerpiece);
# it also exposes GET /health. Live mode (real Gemini 3 + real GitLab) is enabled
# by setting SENTINEL_DEMO=false + GitLab/Vertex env vars at deploy time.
CMD ["python", "-m", "src.sentinel.web"]
