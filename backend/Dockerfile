# Dockerfile para la aplicación Flask con SocketIO
FROM python:3.11-bullseye

WORKDIR /app

# Copiar el archivo de requerimientos e instalar las dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto de la aplicación (ajústalo si es necesario)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
