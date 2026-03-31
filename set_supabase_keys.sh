#!/bin/bash

# Quick Supabase Keys Setup Script
# Run this to set your Supabase keys in the .env file

set -e

echo "🔐 Quick Supabase Keys Setup"
echo "============================="
echo ""

# Create or update .env file
if [ -f ".env" ]; then
    echo "📁 Existing .env file found. Updating Supabase keys..."
else
    echo "📁 Creating new .env file..."
fi

echo ""
echo "Enter your Supabase credentials:"
echo ""

read -p "Supabase Project URL (e.g., https://xyz.supabase.co): " SUPABASE_URL
read -p "Supabase API Key (anon/public): " SUPABASE_KEY

# Extract database info from URL
if [[ $SUPABASE_URL =~ ^https://([a-z0-9]+)\.supabase\.co$ ]]; then
    DB_HOST="${BASH_REMATCH[1]}.supabase.co"
    
    echo ""
    echo "Database connection details:"
    read -p "Database Username [postgres]: " DB_USER
    DB_USER=${DB_USER:-postgres}
    
    read -p "Database Password: " -s DB_PASSWORD
    echo ""
    
    read -p "Database Name [CryptoTrading]: " DB_NAME
    DB_NAME=${DB_NAME:-CryptoTrading}
    
    # Update or create .env file
    if [ -f ".env" ]; then
        # Update existing .env
        grep -v "SUPABASE_\|DB_\|DATABASE_URL" .env > .env.tmp
        mv .env.tmp .env
    fi
    
    # Append Supabase config
    cat >> .env << EOF

# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_KEY=$SUPABASE_KEY
DB_HOST=$DB_HOST
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME
EOF
    
    echo ""
    echo "✅ Supabase keys saved to .env file!"
    echo ""
    echo "To use in Python:"
    echo "----------------"
    echo "1. Install: pip install python-dotenv psycopg2-binary"
    echo "2. In your code:"
    echo ""
    cat << 'PYEOF'
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

# Access your keys
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
PYEOF
    
    echo ""
    echo "🔒 Remember: Never commit .env to git! Add to .gitignore:"
    echo "echo '.env' >> .gitignore"
    
else
    echo "❌ Invalid URL format. Expected: https://xyz.supabase.co"
fi