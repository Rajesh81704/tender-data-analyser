import redis
import os

class RedisClient:
    def __init__(self):
        try:
            # Check if Redis credentials are provided
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_username = os.getenv("REDIS_USERNAME", None)
            redis_password = os.getenv("REDIS_PASSWORD", None)
            
            # Create Redis client with authentication
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                username=redis_username,
                password=redis_password,
                db=int(os.getenv("REDIS_DB", "0")),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.client.ping()
            self.enabled = True
            print(f"Redis connected successfully to {redis_host}:{redis_port}")
        except Exception as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.client = None
    
    def get(self, key):
        if not self.enabled:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def set(self, key, value, ex=None):
        if not self.enabled:
            return False
        try:
            return self.client.set(key, value, ex=ex)
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def delete(self, key):
        if not self.enabled:
            return False
        try:
            return self.client.delete(key)
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key):
        if not self.enabled:
            return False
        try:
            return self.client.exists(key)
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    def flushdb(self):
        """Clear all keys in the current database"""
        if not self.enabled:
            return False
        try:
            return self.client.flushdb()
        except Exception as e:
            print(f"Redis FLUSHDB error: {e}")
            return False
    
    def close(self):
        if self.enabled and self.client:
            try:
                self.client.close()
            except:
                pass

# Singleton instance
redis_client = RedisClient()

