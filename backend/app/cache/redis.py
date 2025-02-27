import redis
import json


class RedisWrapper:
    def __init__(self, redis_host="localhost", redis_port=6379, db=0):
        # Initialize Redis client
        self.db = db    
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    def __getitem__(self, key): 
        # Retrieve and deserialize the value from Redis
        value = self.redis.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in Redis")
        return json.loads(value)
    

    def __delitem__(self, key):
        # Delete the key from Redis
        if not self.redis.delete(key):
            raise KeyError(f"Key {key} not found in Redis")

    def __contains__(self, key):
        # Check if the key exists in Redis
        return self.redis.exists(key)

    def __len__(self):
        # Count the total number of keys in Redis
        return self.redis.dbsize()

    def keys(self):
        # Retrieve all keys
        return self.redis.keys()

    def get(self, key, default=None):
        # Retrieve a value or return a default if not found
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    
    def set(self, key, value, ttl=None):
        # Set a value
        self.redis.set(key, json.dumps(value), ex=ttl)

    def delete_by_prefix(self, prefix: str):
        """Delete all keys that start with a given prefix."""
        keys = self.redis.keys(f"{prefix}*")
        if keys:
            self.redis.delete(*keys)


    def clear(self):
        # Clear all keys in the current Redis database
        self.redis.flushdb()
