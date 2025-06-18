# frontend/Dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Kör i dev‐läge utan build
EXPOSE 3000
CMD ["npm", "run", "dev"]
