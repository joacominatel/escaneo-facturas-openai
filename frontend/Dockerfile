# Etapa 1: Construir la aplicación Next.js
FROM node:22.14-alpine3.20 AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Establecer la variable de entorno para la API (durante la compilación)
ENV NEXT_PUBLIC_API_URL=http://backend:5000

# Construir la aplicación
RUN npm run build

# Etapa 2: Imagen de producción
FROM node:22.14-alpine3.20

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar solo dependencias de producción
RUN npm install --production

# Copiar artefactos de construcción desde la etapa anterior
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

# Establecer variables de entorno para producción
ENV NEXT_PUBLIC_API_URL=http://backend:5000
ENV NODE_ENV=production

# Exponer el puerto 3000
EXPOSE 3000

# Ejecutar la aplicación
CMD ["npm", "start"]
