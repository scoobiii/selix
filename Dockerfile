FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY src/ ./src/
COPY .env.example .env

ENV PYTHONPATH=/app
ENV PORT=5000

EXPOSE 5000
CMD exec gunicorn src.api.main_v4:app -b 0.0.0.0:${PORT} -w 2 --timeout 120
