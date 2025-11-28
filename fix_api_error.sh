#!/bin/bash
# Auto-generated fix script for API Provider Error

echo "Applying fixes for API Provider Error..."

# Fix 1: Set Hugging Face API Token
echo "Setting Hugging Face API Token..."
read -p "Enter your Hugging Face API token: " hf_token
export HF_API_TOKEN="$hf_token"
export HUGGINGFACE_HUB_TOKEN="$hf_token"

# Add to .env file
echo "HF_API_TOKEN=$hf_token" >> .env
echo "HUGGINGFACE_HUB_TOKEN=$hf_token" >> .env

# Fix 2: Configure AI Features
echo "Configuring AI features..."
echo "USE_AI_FEATURES=true" >> .env
echo "USE_HUGGINGFACE_API=true" >> .env

# Fix 3: Add Fallback Configuration
echo "Adding fallback configuration..."
cat >> .env << 'EOF'

# Fallback Configuration
USE_LOCAL_MODELS=true
ENABLE_FALLBACK_RECOMMENDATIONS=true
DISABLE_EXTERNAL_AI_ON_ERROR=true
EOF

echo "Fixes applied successfully!"
echo ""
echo "Next steps:"
echo "1. Restart your application"
echo "2. Test the API endpoints"
echo "3. Check logs for remaining errors"
