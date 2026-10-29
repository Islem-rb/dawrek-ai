# Used by Render (free plan) or any Docker host. Hosts inject PORT; 7860 is the local default.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PORT=7860
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend backend
COPY frontend frontend
COPY data data

# Run as a non-root user
RUN useradd -m -u 1000 user && chown -R user /app
USER user

EXPOSE 7860
CMD ["python", "-m", "backend.main"]
