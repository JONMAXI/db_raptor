# Usa imagen oficial Python
FROM python:3.9-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia archivos
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expone el puerto que usará Cloud Run
EXPOSE 8080

# Ejecuta la app
CMD ["python", "main.py"]
