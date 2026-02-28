import redis
import os

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD", None),
            decode_responses=True
        )
    
    def get(self, key):
        return self.client.get(key)
    
    def set(self, key, value, ex=None):
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key):
        return self.client.delete(key)
    
    def exists(self, key):
        return self.client.exists(key)
    
    def close(self):
        self.client.close()

# Singleton instance
redis_client = RedisClient()
