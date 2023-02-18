import os

REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_PORT = os.getenv("REDIS_PORT", default="6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
METRICS_STREAM = os.getenv("METRICS_STREAM", default="metrics")
HOST = os.getenv("WS_HOST", default="127.0.0.1:8000")
WS_PROTOCOL = os.getenv("WS_PROTOCOL", default="ws")
