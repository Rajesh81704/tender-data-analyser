"""
Script to run database schema migration
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('app/.env')

def run_migration():
    """Execute the schema fix SQL"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", os.getenv("DB_HOST", "localhost")),
            port=os.getenv("PGPORT", os.getenv("DB_PORT", "5432")),
            database=os.getenv("PGDATABASE", os.getenv("DB_NAME", "mydb")),
            user=os.getenv("PGUSER", os.getenv("DB_USER", "postgres")),
            password=os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "")),
        )
        
        cursor = conn.cursor()
        
        # Read SQL file
        with open('fix_schema.sql', 'r') as f:
            sql_script = f.read()
        
        print("Executing migration...")
        
        # Execute SQL script
        cursor.execute(sql_script)
        conn.commit()
        
        print("✓ Migration completed successfully!")
        
        # Verify changes
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'TENDER_DATA_DTLS' 
            AND column_name = 'tndr_pk'
        """)
        result = cursor.fetchone()
        
        if result:
            print(f"✓ Verified: tndr_pk column added to TENDER_DATA_DTLS ({result[1]})")
        else:
            print("⚠ Warning: Could not verify tndr_pk column")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()
