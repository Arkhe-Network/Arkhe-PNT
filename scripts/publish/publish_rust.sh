#!/bin/bash
# publish_rust.sh - Publica o SDK Rust no crates.io

echo "🚀 Publishing Rust SDK..."

# Verificar se estamos no diretório correto
if [ ! -f "Cargo.toml" ]; then
    echo "❌ Error: Run from sdks/rust-archimedes directory"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: There are uncommitted changes. Please commit first."
    exit 1
fi

# Verificar se o crate está limpo
echo "🧹 Running cargo check..."
if ! cargo check; then
    echo "❌ Error: cargo check failed"
    exit 1
fi

echo "🧪 Running tests..."
if ! cargo test; then
    echo "❌ Error: Tests failed"
    exit 1
fi

# Verificar se já existe uma versão no crates.io
echo "📦 Checking current version..."
current_version=$(grep '^version =' Cargo.toml | sed 's/version = "\(.*\)"/\1/')

echo "📝 Current version: $current_version"
echo "📝 Enter new version (current: $current_version):"
read new_version

if [ -z "$new_version" ]; then
    echo "❌ Error: Version cannot be empty"
    exit 1
fi

# Atualizar versão no Cargo.toml
sed -i "s/version = \"$current_version\"/version = \"$new_version\"/" Cargo.toml

echo "📤 Publishing to crates.io..."
if cargo publish --dry-run; then
    echo "🧪 Dry run successful. Publishing for real..."
    cargo publish
    echo "✅ Rust SDK published to crates.io!"
    echo "   Available at: https://crates.io/crates/archimedes-agent"
else
    echo "❌ Dry run failed. Fix issues and try again."
    exit 1
fi