FROM python:3.13-slim AS base

WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia todo o backend
COPY . .

# Dá permissão de execução para o entrypoint
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

# Define entrypoint
CMD ["./docker-entrypoint.sh"]
