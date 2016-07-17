import os
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

# get the environment variable, if not available, set it to default
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
