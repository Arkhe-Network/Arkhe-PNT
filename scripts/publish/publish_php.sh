#!/bin/bash
# publish_php.sh - Publica o SDK PHP no Packagist

echo "🚀 Publishing PHP SDK..."

# Verificar se estamos no diretório correto
if [ ! -f "composer.json" ]; then
    echo "❌ Error: Run from sdks/php directory"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: There are uncommitted changes. Please commit first."
    exit 1
fi

# Verificar se o composer.json é válido
echo "📦 Validating composer.json..."
if ! composer validate; then
    echo "❌ Error: composer.json is invalid"
    exit 1
fi

# Verificar versão atual
current_version=$(grep '"version"' composer.json | sed 's/.*"version": "\(.*\)".*/\1/')

echo "📝 Current version: $current_version"
echo "📝 Enter new version (current: $current_version):"
read new_version

if [ -z "$new_version" ]; then
    echo "❌ Error: Version cannot be empty"
    exit 1
fi

# Atualizar versão no composer.json
sed -i "s/\"version\": \"$current_version\"/\"version\": \"$new_version\"/" composer.json

# Commit e push
echo "📝 Committing version bump..."
git add composer.json
git commit -m "Bump version to $new_version"

echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ PHP SDK published!"
echo "   It will be available on Packagist after the webhook processes it:"
echo "   composer require arkhe/archimedes-agent:$new_version"
echo ""
echo "   Note: Make sure the GitHub webhook is configured in Packagist"