from ...base import BaseKeyManager
from ...base.types import TOTAL_MODELS_NAME


class NonKeyManager(BaseKeyManager):
    def __init__(self) -> None:
        pass

    def get_allow_models(self, api_key: str) -> list[str]:
        return [TOTAL_MODELS_NAME]

    def set_allow_model(self, key_name: str, model: str) -> bool:
        # log : non_key_manager not allowed to set allow model
        return False

    def set_api_key(self, key_name: str) -> str:
        # log : non_key_manager not allowed to set api key
        return ""

    def get_api_key(self, key_name: str) -> str:
        # log : non_key_manager not allowed to get api key
        return ""