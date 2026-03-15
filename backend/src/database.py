"""MongoDB connection and client initialization."""

from dotenv import load_dotenv
import os
import threading
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

_mongo_client = None
_lock = threading.Lock()


def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        with _lock:
            if _mongo_client is None:
                uri = os.environ.get("MONGODB_URI")
                if uri:
                    if uri.startswith("mongodb+srv://"):
                        _mongo_client = MongoClient(uri, server_api=ServerApi("1"))
                    else:
                        _mongo_client = MongoClient(uri)
                else:
                    host = os.environ["DB_HOST"]
                    username = os.environ["DB_USERNAME"]
                    password = os.environ["DB_PASSWORD"]
                    _mongo_client = MongoClient(
                        f"mongodb+srv://{username}:{password}@{host}/?retryWrites=true&w=majority",
                        server_api=ServerApi("1"),
                    )
    return _mongo_client


# Backwards-compatible module-level alias used by api.py
class _LazyClient:
    """Proxy that defers MongoClient creation until first attribute access."""
    def __getattr__(self, name):
        return getattr(get_mongo_client(), name)
    def __getitem__(self, name):
        return get_mongo_client()[name]

mongo_client = _LazyClient()
