# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./

RUN npm ci --prefer-offline --no-audit 2>/dev/null || npm install

COPY . .

RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./

RUN npm ci --prefer-offline --no-audit 2>/dev/null || npm install

COPY --from=builder /app/.next /app/.next

EXPOSE 3000

CMD ["npm", "start"]
