FROM node:20-alpine

WORKDIR /app

# Instalar dependências para o ReportLab (Python)
RUN apk add --no-cache python3 py3-pip g++ make

# Criar ambiente virtual para o Python
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar reportlab
RUN pip install reportlab

COPY package*.json ./
COPY arkhe-chain-node/package*.json ./arkhe-chain-node/
COPY arkhe-chain-node/apps/api-nest/package*.json ./arkhe-chain-node/apps/api-nest/
COPY arkhe-chain-node/apps/telemetry-fastify/package*.json ./arkhe-chain-node/apps/telemetry-fastify/
COPY arkhe-chain-node/apps/express-bridge/package*.json ./arkhe-chain-node/apps/express-bridge/
COPY arkhe-chain-node/packages/shared/package*.json ./arkhe-chain-node/packages/shared/

RUN cd arkhe-chain-node && npm install

COPY . .

# Gerar Prisma Client
RUN cd arkhe-chain-node/apps/api-nest && npx prisma generate

# 13/ Run as non-root user
RUN addgroup -S arkhe && adduser -S arkhe -G arkhe
RUN chown -R arkhe:arkhe /app
USER arkhe

EXPOSE 3000 3001

CMD ["npm", "run", "dev", "--prefix", "arkhe-chain-node"]
