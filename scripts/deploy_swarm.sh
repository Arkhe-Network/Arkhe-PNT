#!/bin/bash

# Arkhe(n) Swarm Deployment Script
# Este script inicializa o Docker Swarm e implanta a stack da Arkhe(n).

set -e

echo "🜏 Iniciando Materialização no Docker Swarm..."

# 1. Inicializar o Swarm (se não estiver inicializado)
if ! docker info | grep -q "Swarm: active"; then
    echo "Inicializando Docker Swarm..."
    docker swarm init
else
    echo "Docker Swarm já está ativo."
fi

# 2. Criar o segredo da tesouraria (se não existir)
# Em produção, a chave deve vir de um KMS ou ser injetada de forma segura.
# Este é um exemplo de como criar o segredo a partir de uma variável de ambiente.
if ! docker secret ls | grep -q "treasury_key"; then
    if [ -z "$ARKHE_TREASURY_PK" ]; then
        echo "ERRO: Variável ARKHE_TREASURY_PK não definida para criar o segredo inicial."
        exit 1
    fi
    echo "Criando segredo treasury_key..."
    echo "$ARKHE_TREASURY_PK" | docker secret create treasury_key -
else
    echo "Segredo treasury_key já existe."
fi

# 3. Fazer login no GitHub Container Registry (GHCR)
if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_ACTOR" ]; then
    echo "Autenticando no GHCR..."
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin
else
    echo "Aviso: GITHUB_TOKEN ou GITHUB_ACTOR não definidos. O pull de imagens privadas pode falhar."
fi

# 4. Implantar a stack
echo "Implantando a stack Arkhe(n)..."
export GITHUB_REPOSITORY_OWNER=${GITHUB_REPOSITORY_OWNER:-"seu-usuario"}
docker stack deploy -c docker-compose.swarm.yml arkhe-stack

echo "🜏 Materialização concluída. A Arkhe(n) está viva no Swarm."
echo "Verifique o status com: docker stack services arkhe-stack"
