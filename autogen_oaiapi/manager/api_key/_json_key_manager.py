import json
from pydantic import TypeAdapter
from ...base import BaseKeyManager, APIKeyStore, DefaultAPIKeyStore

class JsonKeyManager(BaseKeyManager):
    def __init__(self, json_path: str) -> None:
        key_store = DefaultAPIKeyStore()
        super().__init__(key_store=key_store)
        with open(json_path, "r") as json_file:
            key_store: APIKeyStore = TypeAdapter(APIKeyStore).validate_json(
                json_file.read(), strict=True
            )
        self._key_store.set_api_key_entry_batch(key_store.keys)
