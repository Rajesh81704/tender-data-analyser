"""
Script to check actual database columns
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('app/.env')

def check_columns():
    """Check actual columns in TENDER_DATA_DTLS table"""
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
        
        # Check TENDER_DATA_DTLS columns
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'TENDER_DATA_DTLS'
            ORDER BY ordinal_position
        """)
        
        print("\n=== TENDER_DATA_DTLS Columns ===")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Check DISTRICT_DETAILS columns
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'DISTRICT_DETAILS'
            ORDER BY ordinal_position
        """)
        
        print("\n=== DISTRICT_DETAILS Columns ===")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Check DEPT_DTLS columns
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'DEPT_DTLS'
            ORDER BY ordinal_position
        """)
        
        print("\n=== DEPT_DTLS Columns ===")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_columns()
