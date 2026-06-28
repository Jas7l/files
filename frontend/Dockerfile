FROM node:20-alpine

WORKDIR /app

# Копируем package.json и устанавливаем ВСЕ зависимости
COPY package*.json ./
RUN npm install

# Копируем остальной код
COPY . .

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN echo "VITE_API_URL=${VITE_API_URL}" > .env

EXPOSE 5173

# Запускаем dev сервер
CMD ["npm", "run", "dev", "--", "--host"]