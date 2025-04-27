from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .utils import generate_key

class APIKeyEntry(BaseModel):
    api_key: str = Field(..., description="API Key")
    allowed_models: List[str] = Field(default_factory=list, description="allowed models for this key, '*' for all models")
    is_active: bool = Field(default=True, description="API Key active status")
    description: str | None = Field(default=None, description="Key description optional")


class APIKeyStore(BaseModel):
    keys: Dict[str, APIKeyEntry] = Field(..., description="API Key entries")


class BaseAPIKeyStore(ABC):
    @abstractmethod
    def get_api_key_entry(self, api_key: str) -> Optional[APIKeyEntry]:
        """Get the API key."""
        ...

    @abstractmethod
    def set_api_key(self, key_name: str, api_key: str, description: str|None=None) -> APIKeyEntry:
        """Set a new API key."""
        ...

    @abstractmethod
    def set_model_to_api_key(self, key_name: str, model: str) -> bool:
        """Set the list of allowed models for an API key."""
        ...

    @abstractmethod
    def set_api_key_active_status(self, key_name: str, is_active: bool) -> None:
        """Set the active status of an API key."""
        ...

    @abstractmethod
    def get_all_api_key_entries(self) -> List[tuple[str,APIKeyEntry]]:
        """Get all API key entries."""
        ...


class DefaultAPIKeyStore(BaseAPIKeyStore):
    def __init__(self) -> None:
        self._api_keys: Dict[str, APIKeyEntry] = {}
        self._key2name: Dict[str, str] = {}

    def set_api_key_entry_batch(self, key_entries: Dict[str, APIKeyEntry]) -> None:
        self._api_keys.update(key_entries)
        for key_name, entry in key_entries.items():
            self._key2name[entry.api_key] = key_name

    def set_api_key_entry(self, key_name: str, key_entry: APIKeyEntry) -> None:
        self._api_keys[key_name] = key_entry
        self._key2name[key_entry.api_key] = key_name

    def get_api_key_entry(self, api_key: str) -> Optional[APIKeyEntry]:
            return self._api_keys.get(self._key2name.get(api_key, ""), None)

    def set_api_key(self, key_name: str, api_key: str, description: str|None=None) -> APIKeyEntry:
        entry = APIKeyEntry(
            api_key=api_key,
            allowed_models=[],
            description=description,
        )
        self._api_keys[key_name] = entry
        self._key2name[api_key] = key_name
        return entry

    def set_model_to_api_key(self, key_name: str, model: str) -> bool:
        if key_name not in self._api_keys:
            return False
        entry = self._api_keys[key_name]
        if model not in entry.allowed_models:
            entry.allowed_models.append(model)
            return True
        return False

    def set_api_key_active_status(self, key_name: str, is_active: bool) -> None:
        if key_name in self._api_keys:
            self._api_keys[key_name].is_active = is_active

    def get_all_api_key_entries(self) -> List[tuple[str,APIKeyEntry]]:
        return list(self._api_keys.items())


class BaseKeyManager(ABC):
    def __init__(self, key_store: BaseAPIKeyStore) -> None:
        self._key_store: BaseAPIKeyStore = key_store

    def get_allow_models(self, api_key: str) -> List[str]:
        """Get the list of allowed models."""
        key_entry = self._key_store.get_api_key_entry(api_key)
        return key_entry.allowed_models if key_entry else []

    def set_allow_model(self, key_name: str, model: str) -> bool:
        """Set the list of allowed models."""
        return self._key_store.set_model_to_api_key(key_name, model)

    def set_api_key(self, key_name: str) -> str:
        """Set a new API key."""
        api_key = generate_key()
        self._key_store.set_api_key(key_name, api_key)
        return api_key

    def get_api_key(self, key_name: str) -> str:
        """Get the API key."""
        key_entry = self._key_store.get_api_key_entry(key_name)
        if key_entry:
            return key_entry.api_key
        else:
            return "BASE_API_KEY"