FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py \
    FLASK_CONFIG=production \
    DISABLE_AUTO_SETUP=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10000 academy

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=academy:academy . .
RUN mkdir -p /app/instance && chown -R academy:academy /app/instance

USER academy
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "flask db upgrade && flask seed && gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app"]
