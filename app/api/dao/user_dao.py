import psycopg2
from app.api.models.user import UserSignup
from app.api.utils.database import get_db


class UserDAO:
    def get_by_username(self, username: str):
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        cursor.close()
        db.release_connection(conn)
        
        if result:
            return {"id": result[0], "username": result[1], "email": result[2], "password": result[3]}
        return None

    def create(self, user: UserSignup, hashed_password: str):
        db = get_db()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id, username, email",
            (user.username, user.email, hashed_password)
        )
        result = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        db.release_connection(conn)
        
        return {"id": result[0], "username": result[1], "email": result[2]}
