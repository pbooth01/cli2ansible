FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create virtual environments in Docker
RUN poetry config virtualenvs.create false

# Install dependencies (including ansible tools for Linux)
RUN poetry install --only main --no-root --no-interaction --no-ansi

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Add src to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Create artifacts directory
RUN mkdir -p /app/artifacts

# Run as non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "cli2ansible.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
