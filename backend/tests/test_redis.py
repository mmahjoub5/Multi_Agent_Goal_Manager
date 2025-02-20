from app.cache.redis  import RedisWrapper
import redis
import json
import pytest

def test_set_redis_wrapper():
    wrapper = RedisWrapper()
    # Clear the cache to start with a clean state
    wrapper.clear()
    
    # Check that the Redis cache is accessible (should be empty)
    assert len(wrapper) == 0, "Redis cache should be empty initially"
    
    # Add a value to the Redis cache
    key = "mykey"
    value = {"hello": "world"}
    wrapper.set(key, value)
    
    # Verify that the value was added using the wrapper's get() method
    retrieved = wrapper.get(key)
    assert retrieved == value, "Retrieved value should match the inserted value"
    
    # Optionally, verify directly via a redis client (value is stored as JSON)
    redis_client = redis.Redis(host="localhost", port=6379, db=wrapper.db, decode_responses=True)
    raw_value = redis_client.get(key)
    assert raw_value == json.dumps(value), "Raw value in Redis should match the JSON serialized value"
    
    print("All tests passed.")



def test_delete_redis_wrapper():
    wrapper = RedisWrapper()
    # Clear the cache to start with a clean state
    wrapper.clear()
    
    # Add a value to the Redis cache
    key = "mykey"
    value = {"hello": "world"}
    wrapper.set(key, value)
    
    # Verify that the value was added using the wrapper's get() method
    retrieved = wrapper.get(key)
    assert retrieved == value, "Retrieved value should match the inserted value"
    
    # Delete the key from the Redis cache
    del wrapper[key]
    
    # Verify that the key was deleted by accessing it with bracket notation, which should raise KeyError
    with pytest.raises(KeyError):
        _ = wrapper[key]
    
    print("All tests passed.")

def test_if_key_in_redis():
    wrapper = RedisWrapper()
    # Clear the cache to start with a clean state
    wrapper.clear()
    
    # Add a value to the Redis cache
    key = "mykey"
    value = {"hello": "world"}
    wrapper.set(key, value)
    
    # Verify that the key is in the Redis cache
    assert key in wrapper, "Key should be in Redis cache"
    
    # Delete the key from the Redis cache
    del wrapper[key]
    
    # Verify that the key is no longer in the Redis cache
    assert key not in wrapper, "Key should not be in Redis cache after deletion"
    
    print("All tests passed.")