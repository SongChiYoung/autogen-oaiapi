import json
from ...base import BaseKeyManager
from ...base import BaseKeyManager, DefaultAPIKeyStore


class MemoryKeyManager(BaseKeyManager):
    def __init__(self) -> None:
        key_store = DefaultAPIKeyStore()
        super().__init__(key_store=key_store)
