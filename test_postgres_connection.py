#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection for Vercel deployment.
"""
import os
import sys
import json

def load_env_from_file():
    """Load environment variables from .env.development.local file."""
    env_vars = {}
    try:
        with open('.env.development.local', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"\'')
        return env_vars
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return {}

def test_postgres_connection():
    """Test PostgreSQL connection."""
    try:
        # Load environment variables from file
        env_vars = load_env_from_file()
        
        # Check if we have PostgreSQL credentials
        if 'mail_scheduler_DATABASE_URL' not in env_vars:
            print("No PostgreSQL database URL found in .env.development.local")
            return False
            
        # Print connection info (with password masked)
        db_url = env_vars['mail_scheduler_DATABASE_URL']
        masked_url = db_url
        if '@' in db_url:
            prefix, rest = db_url.split('@', 1)
            if ':' in prefix:
                user_part, _ = prefix.rsplit(':', 1)
                masked_url = f"{user_part}:****@{rest}"
        
        print(f"Database URL: {masked_url}")
        
        # Try to connect
        import psycopg2
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully connected to PostgreSQL database")
        print(f"Test query result: {result}")
        return True
    except ImportError:
        print("❌ psycopg2 module not found. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    print("Testing Vercel PostgreSQL Connection")
    print("-" * 40)
    
    # Check if env file exists
    if not os.path.exists('.env.development.local'):
        print("❌ No .env.development.local file found")
        print("💡 Run 'vercel env pull .env.development.local' to download environment variables")
        sys.exit(1)
        
    # Test connection
    if test_postgres_connection():
        print("\n✅ PostgreSQL connection successful!")
        print("Your Vercel deployment should work correctly with PostgreSQL")
    else:
        print("\n❌ PostgreSQL connection failed")
        print("Check your Vercel environment variables and database setup")
