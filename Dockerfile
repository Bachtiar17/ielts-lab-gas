# Cloud Run / Google AI Studio Production Dockerfile (Single-Port Node.js Next.js)
FROM node:22-slim AS builder

WORKDIR /app

# Install root dependencies cleanly (no npm workspaces required)
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

# Copy Next.js frontend app & verified content bundle
COPY frontend ./frontend

# Build optimized production Next.js bundle (includes all 19 /api/* routes)
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-slim AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/frontend ./frontend

EXPOSE 3000

CMD ["sh", "-c", "npx next start frontend -H 0.0.0.0 -p ${PORT:-3000}"]
