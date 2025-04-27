from ...base import BaseKeyManager
from ...base.types import TOTAL_MODELS_NAME


class NonKeyManager(BaseKeyManager):
    """
    NonKeyManager is a key manager that does not manage API keys.
    It is used to disable API key management and restrict access to models.
    """
    def __init__(self) -> None:
        pass

    def get_allow_models(self, api_key: str) -> list[str]:
        """
        Get the list of allowed models for the given API key.
        Args:
            api_key (str): The API key to look up. BUt this is not used in NonKeyManager.
        Returns:
            list[str]: A list of allowed models for the API key.
        """
        return [TOTAL_MODELS_NAME]

    def set_allow_model(self, key_name: str, model: str) -> bool:
        """
        Set the list of allowed models for the given API key.
        Args:
            key_name (str): The name of the API key. But this is not used in NonKeyManager.
            model (str): The model to allow for this API key. But this is not used in NonKeyManager.
        Returns:
            bool: False, as setting allowed models is not allowed in NonKeyManager.
        """
        # log : non_key_manager not allowed to set allow model
        return False

    def set_api_key(self, key_name: str) -> str:
        """
        Set the API key for the given key name.
        Args:
            key_name (str): The name of the API key. But this is not used in NonKeyManager.
        Returns:
            str: An empty string, as setting API keys is not allowed in NonKeyManager.
        """
        # log : non_key_manager not allowed to set api key
        return ""

    def get_api_key(self, key_name: str) -> str:
        """
        Get the API key for the given key name.
        Args:
            key_name (str): The name of the API key. But this is not used in NonKeyManager.
        Returns:
            str: An empty string, as getting API keys is not allowed in NonKeyManager.
        """
        # log : non_key_manager not allowed to get api key
        return ""