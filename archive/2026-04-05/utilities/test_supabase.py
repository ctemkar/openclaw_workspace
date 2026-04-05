#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

print("🧪 Testing Supabase Connection...")
print("=" * 40)

# Check environment variables
print("Checking environment variables:")
print(f"  SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Missing'}")
print(f"  SUPABASE_KEY: {'✅ Set' if os.getenv('SUPABASE_KEY') else '❌ Missing'}")
print(f"  DB_HOST: {'✅ Set' if os.getenv('DB_HOST') else '❌ Missing'}")
print(f"  DB_PORT: {'✅ Set' if os.getenv('DB_PORT') else '❌ Missing'}")
print(f"  DB_NAME: {'✅ Set' if os.getenv('DB_NAME') else '❌ Missing'}")
print(f"  DB_USER: {'✅ Set' if os.getenv('DB_USER') else '❌ Missing'}")
print(f"  DB_PASSWORD: {'✅ Set' if os.getenv('DB_PASSWORD') else '❌ Empty (might be OK)'}")

print("\n" + "=" * 40)
print("Attempting connection to Supabase...")

try:
    # Connect to Supabase
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD') or ''
    )
    
    # Get database info
    cursor = conn.cursor()
    
    # Check PostgreSQL version
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ PostgreSQL Version: {version.split(',')[0]}")
    
    # Check current database
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()[0]
    print(f"✅ Connected to database: {db_name}")
    
    # List tables (if any)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    if tables:
        print(f"✅ Found {len(tables)} table(s):")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("📭 No tables found in database (this is normal for new database)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 40)
    print("🎉 SUPABASE CONNECTION SUCCESSFUL!")
    print(f"Database: {db_name}")
    print(f"Host: {os.getenv('DB_HOST')}")
    
except psycopg2.OperationalError as e:
    print(f"\n❌ CONNECTION FAILED: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if database 'CryptoTrading' exists in Supabase")
    print("2. Verify your password (might be empty)")
    print("3. Check if IP is allowed in Supabase dashboard")
    print("4. Try connecting with: psql postgresql://postgres:@dxzawamxhvlrxtrvziao.supabase.co:5432/CryptoTrading")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "=" * 40)
print("Next steps:")
print("1. Run: pip install psycopg2-binary python-dotenv")
print("2. Test sync: python -c 'from supabase_integration import test_supabase_connection; test_supabase_connection()'")