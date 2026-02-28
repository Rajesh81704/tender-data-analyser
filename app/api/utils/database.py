import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables - find .env file in app directory
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try loading from app/.env
    load_dotenv('app/.env')

class Database:
    def __init__(self):
        self.pool = None
    
    def _initialize_pool(self):
        if self.pool is None:
            # Get SSL mode
            sslmode = os.getenv("PGSSLMODE", "prefer")
            
            # Build connection parameters
            conn_params = {
                "host": os.getenv("PGHOST", os.getenv("DB_HOST", "localhost")),
                "port": os.getenv("PGPORT", os.getenv("DB_PORT", "5432")),
                "database": os.getenv("PGDATABASE", os.getenv("DB_NAME", "mydb")),
                "user": os.getenv("PGUSER", os.getenv("DB_USER", "postgres")),
                "password": os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "")),
                "sslmode": sslmode,
            }
            
            # Add channel binding if specified (required for Neon)
            channel_binding = os.getenv("PGCHANNELBINDING")
            if channel_binding:
                conn_params["channel_binding"] = channel_binding
            
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **conn_params
            )
    
    def get_connection(self):
        if self.pool is None:
            self._initialize_pool()
        return self.pool.getconn()
    
    def release_connection(self, conn):
        self.pool.putconn(conn)
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.fetchall()
        finally:
            self.release_connection(conn)
    
    def close_all(self):
        if self.pool:
            self.pool.closeall()

# Singleton instance - use get_db() to access
_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
