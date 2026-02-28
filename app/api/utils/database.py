import psycopg2
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('app/.env')

class Database:
    def __init__(self):
        self.pool = None
    
    def _initialize_pool(self):
        if self.pool is None:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=os.getenv("PGHOST", os.getenv("DB_HOST", "localhost")),
                port=os.getenv("PGPORT", os.getenv("DB_PORT", "5432")),
                database=os.getenv("PGDATABASE", os.getenv("DB_NAME", "mydb")),
                user=os.getenv("PGUSER", os.getenv("DB_USER", "postgres")),
                password=os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", "")),
                sslmode=os.getenv("PGSSLMODE", "prefer")
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
