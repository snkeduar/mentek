FROM python:3.11-slim

WORKDIR /app

# Instala dependencias del sistema y Alembic
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install alembic

# Copia requirements y instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto (incluyendo alembic.ini y la carpeta alembic)
COPY . .

# Comando para iniciar (ejecuta migraciones y luego la app)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]