#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2
import sys

# Load environment variables
load_dotenv()

print("Testing Supabase connection...")

try:
    # Try to connect with timeout
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD') or '',
        connect_timeout=5
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()[0]
    
    print(f"✅ SUCCESS! Connected to database: {db_name}")
    print(f"   Host: {os.getenv('DB_HOST')}")
    print(f"   Database: {os.getenv('DB_NAME')}")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ CONNECTION FAILED: {e}")
    print("\nCommon issues:")
    print("1. Database 'CryptoTrading' doesn't exist")
    print("2. Password required but not set")
    print("3. IP not allowed in Supabase")
    print("4. Network/firewall issue")
    
    # Try to connect to default 'postgres' database
    print("\nTrying default 'postgres' database...")
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='postgres',  # Try default database
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD') or '',
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        print(f"✅ Connected to default database: {db_name}")
        
        # List databases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()
        print(f"\nAvailable databases:")
        for db in databases:
            print(f"  - {db[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e2:
        print(f"❌ Also failed: {e2}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")