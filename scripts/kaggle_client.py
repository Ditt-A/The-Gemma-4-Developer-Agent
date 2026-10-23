"""Lazy Kaggle authentication. Importing build or status helpers reads no secrets."""
import json
import os
from pathlib import Path


def api_client(credential_file=None):
    if credential_file:
        path = Path(credential_file).expanduser()
        credentials = json.loads(path.read_text(encoding="utf-8-sig"))
        if not credentials.get("username") or not credentials.get("key"):
            raise ValueError("The supplied Kaggle credential file needs username and key")
        os.environ["KAGGLE_USERNAME"] = credentials["username"]
        os.environ["KAGGLE_KEY"] = credentials["key"]
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    return api


def plain(value):
    if hasattr(value, "to_dict"):
        return plain(value.to_dict())
    if isinstance(value, dict):
        return {key: plain(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(child) for child in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
