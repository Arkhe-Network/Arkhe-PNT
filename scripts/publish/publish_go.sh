#!/bin/bash
# publish_go.sh - Publica o SDK Go no GitHub

echo "🚀 Publishing Go SDK..."

# Verificar se estamos no diretório correto
if [ ! -f "go.mod" ]; then
    echo "❌ Error: Run from sdks/go directory"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: There are uncommitted changes. Please commit first."
    exit 1
fi

# Criar tag de versão
echo "📝 Enter version (e.g., v1.0.0):"
read version

if [ -z "$version" ]; then
    echo "❌ Error: Version cannot be empty"
    exit 1
fi

# Verificar formato da versão
if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Version must be in format v1.0.0"
    exit 1
fi

echo "🏷️  Creating tag $version..."
git tag "$version"

echo "📤 Pushing tag to GitHub..."
git push origin "$version"

echo "✅ Go SDK published! It will be available at:"
echo "   https://github.com/arkhe/archimedes-agent-go"
echo "   go get github.com/arkhe/archimedes-agent-go@$version"