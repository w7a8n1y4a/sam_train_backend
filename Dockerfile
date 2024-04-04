FROM nvcr.io/nvidia/pytorch:24.01-py3

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.3.0

WORKDIR /app

RUN apt update && apt install -y libpq-dev gcc curl cron python3-dev && rm -rf /var/lib/apt/lists/*

RUN pip install "poetry==$POETRY_VERSION"
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --no-ansi

COPY . .

RUN chmod +x /app/entrypoint.sh

CMD ["/bin/bash", "/app/entrypoint.sh"]
