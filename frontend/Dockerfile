FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV NEXT_PUBLIC_API_URL http://backend:5000/api_v2

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]