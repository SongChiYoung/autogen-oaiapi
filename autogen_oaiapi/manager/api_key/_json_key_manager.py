from pydantic import TypeAdapter
from ...base import BaseKeyManager, APIKeyStore, DefaultAPIKeyStore

class JsonKeyManager(BaseKeyManager):
    """
    JsonKeyManager is a key manager that loads API keys from a JSON file.
    It is used to manage API keys and their associated models.
    """
    def __init__(self, json_path: str) -> None:
        """
        Initialize the JsonKeyManager with a path to a JSON file.
        Args:
            json_path (str): The path to the JSON file containing API keys.
        """
        api_key_store = DefaultAPIKeyStore()
        super().__init__(key_store=api_key_store)
        with open(json_path, "r") as json_file:
            key_store = TypeAdapter(APIKeyStore).validate_json(
                json_file.read(), strict=True
            )
        api_key_store.set_api_key_entry_batch(key_store.keys)
