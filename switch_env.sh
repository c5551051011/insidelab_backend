#!/bin/bash

# =============================================================================
# Environment Switcher for InsideLab Backend
# =============================================================================
# Usage: ./switch_env.sh [dev|prod]

if [ $# -eq 0 ]; then
    echo "🔧 InsideLab Environment Switcher"
    echo ""
    echo "Usage: ./switch_env.sh [dev|prod]"
    echo ""
    echo "Available environments:"
    echo "  dev   - Development environment (default database)"
    echo "  prod  - Production environment (clean database)"
    echo ""
    echo "Current environment:"
    if [ -f .env ]; then
        current_env=$(grep DJANGO_ENVIRONMENT .env | cut -d'=' -f2)
        echo "  DJANGO_ENVIRONMENT=${current_env}"
    else
        echo "  No .env file found"
    fi
    exit 1
fi

case $1 in
    "dev")
        echo "🔄 Switching to Development environment..."
        cp .env.dev .env
        echo "✅ Switched to Development environment"
        echo "   - Database: postgres.aetnyvpjauczqlkihpyc (development data)"
        echo "   - DEBUG: True"
        echo "   - Domain: localhost:8000"
        ;;
    "prod")
        echo "🔄 Switching to Production environment..."
        cp .env.prod .env
        echo "✅ Switched to Production environment"
        echo "   - Database: postgres.zwztxgsxjoutvtwugtrq (clean production)"
        echo "   - DEBUG: False"
        echo "   - Domain: localhost:8000"
        echo ""
        echo "⚠️  Note: This is for local testing of production settings only"
        ;;
    *)
        echo "❌ Invalid environment: $1"
        echo "Available options: dev, prod"
        exit 1
        ;;
esac

echo ""
echo "🚀 You can now run: python manage.py runserver"