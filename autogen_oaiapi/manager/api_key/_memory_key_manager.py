from ...base import BaseKeyManager
from ...base import DefaultAPIKeyStore


class MemoryKeyManager(BaseKeyManager):
    """
    MemoryKeyManager is a key manager that stores API keys in memory.
    It is used to manage API keys and their associated models.
    """
    def __init__(self) -> None:
        """
        Initialize the MemoryKeyManager with a default API key store.
        """
        key_store = DefaultAPIKeyStore()
        super().__init__(key_store=key_store)
