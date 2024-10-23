import os

import redis

redis_host = os.environ.get("REDIS_HOST", "redis")
redis_client = redis.StrictRedis(host=redis_host, port=6379, db=1)


def get_redis_client():
    return redis_client
