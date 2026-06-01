FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install --frozen-lockfile || npm install

COPY . .

# Compilar Next.js en produccion
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
