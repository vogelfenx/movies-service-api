import time
from os import getenv

from redis import Redis

redis_host = getenv("REDIS_HOST", default="localhost")
redis_port = getenv("REDIS_PORT", default=6379)

if __name__ == "__main__":
    redis_client = Redis(host=redis_host, port=redis_port)

    print(f"try redis on {redis_host}:{redis_port}")
    while True:
        print("ping redis")
        if redis_client.ping():
            break
        time.sleep(1)
