import json
import datetime
from .redis_client import redis_client, REDIS_TTL

class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle special types like datetimes.
    """
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        # Handle pandas Timestamps if they appear
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

def normalize_question(question: str) -> str:
    return question.lower().strip()

def make_cache_key(client_id: str, question: str) -> str:
    return f"nl2sql:{client_id}:{normalize_question(question)}"

def get_from_cache(cache_key: str):
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

def set_to_cache(cache_key: str, value: dict):
    """
    Caches a dictionary value in Redis using a custom JSON encoder.
    """
    redis_client.setex(cache_key, REDIS_TTL, json.dumps(value, cls=CustomJSONEncoder))
