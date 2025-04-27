from pydantic import TypeAdapter
from ...base import BaseKeyManager, APIKeyStore, DefaultAPIKeyStore

class JsonKeyManager(BaseKeyManager):
    def __init__(self, json_path: str) -> None:
        api_key_store = DefaultAPIKeyStore()
        super().__init__(key_store=api_key_store)
        with open(json_path, "r") as json_file:
            key_store = TypeAdapter(APIKeyStore).validate_json(
                json_file.read(), strict=True
            )
        api_key_store.set_api_key_entry_batch(key_store.keys)
