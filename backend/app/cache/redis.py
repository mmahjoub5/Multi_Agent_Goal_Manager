import redis
import json

class RedisWrapper:
    def __init__(self, redis_host="localhost", redis_port=6379, db=0):
        # Initialize Redis client
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    def __getitem__(self, key):
        # Retrieve and deserialize the value from Redis
        value = self.redis.get(key)
        if value is None:
            raise KeyError(f"Key {key} not found in Redis")
        return json.loads(value)

    def __setitem__(self, key, value):
        # Serialize and store the value in Redis
        self.redis.set(key, json.dumps(value))

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

    def clear(self):
        # Clear all keys in the current Redis database
        self.redis.flushdb()

# # Example Usage
# ROBOTTABLE = RedisWrapper()

# # Add a robot to ROBOTTABLE
# ROBOTTABLE["robot_1"] = {
#     "Doc": {"id": "robot_1", "name": "RobotOne", "type": "TypeA"},
#     "Task_List": ["task1", "task2"]
# }

# # Retrieve a robot
# print(ROBOTTABLE["robot_1"])

# # Check if a robot exists
# print("robot_1" in ROBOTTABLE)

# # Delete a robot
# del ROBOTTABLE["robot_1"]
