import redis
import os

class RedisClient:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                db=int(os.getenv("REDIS_DB", "0")),
                password=os.getenv("REDIS_PASSWORD", None),
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.client = None
    
    def get(self, key):
        if not self.enabled:
            return None
        try:
            return self.client.get(key)
        except:
            return None
    
    def set(self, key, value, ex=None):
        if not self.enabled:
            return False
        try:
            return self.client.set(key, value, ex=ex)
        except:
            return False
    
    def delete(self, key):
        if not self.enabled:
            return False
        try:
            return self.client.delete(key)
        except:
            return False
    
    def exists(self, key):
        if not self.enabled:
            return False
        try:
            return self.client.exists(key)
        except:
            return False
    
    def close(self):
        if self.enabled and self.client:
            try:
                self.client.close()
            except:
                pass

# Singleton instance
redis_client = RedisClient()
