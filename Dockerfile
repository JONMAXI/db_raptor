FROM python:3.10-slim

# Instalar dependencias del sistema y fuentes básicas para Pillow
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . /app
WORKDIR /app

# Exponer puerto 8080 para Cloud Run
EXPOSE 8080

# Ejecutar la app
CMD ["python", "app.py"]
