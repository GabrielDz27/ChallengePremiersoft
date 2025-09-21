FROM python:3.13-slim AS base

WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copia todo o backend
COPY . .

EXPOSE 8000

# Roda init_db.py e depois main.py
CMD ["sh", "-c", "python ./init_db.py && python ./main.py"]
