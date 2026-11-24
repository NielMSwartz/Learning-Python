FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EXECUTOR_WORKDIR=/tmp/python-academy-exec

WORKDIR /executor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 executor \
    && mkdir -p "$EXECUTOR_WORKDIR" \
    && chown -R executor:executor /executor "$EXECUTOR_WORKDIR"

COPY --chown=executor:executor server.py engine.py sandbox_runner.py ./

USER executor
EXPOSE 9000

CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "2", "--threads", "4", \
     "--timeout", "120", "--graceful-timeout", "10", "server:app"]
