import redis

redis_client = redis.StrictRedis(host="redis", port=6379, db=1)


def get_redis_client():
    return redis_client
