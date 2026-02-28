import redis
import os

class RedisClient:
    def __init__(self):
        # Redis is disabled
        self.enabled = False
        self.client = None
        print("Redis caching is disabled.")
    
    def get(self, key):
        return None
    
    def set(self, key, value, ex=None):
        return False
    
    def delete(self, key):
        return False
    
    def exists(self, key):
        return False
    
    def flushdb(self):
        return False
    
    def close(self):
        pass

# Singleton instance
redis_client = RedisClient()

