FROM python:3.10-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Instalar pip packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . /app
WORKDIR /app

# Exponer puerto
EXPOSE 8080

# Ejecutar la app
CMD ["python", "app.py"]