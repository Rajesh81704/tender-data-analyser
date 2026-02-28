from app.api.utils.redis_client import redis_client

try:
    redis_client.flushdb()
    print("Redis cache cleared successfully!")
except Exception as e:
    print(f"Error clearing cache: {e}")
