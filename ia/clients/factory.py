from ia.clients.jan import JanClient
from ia.config import IASettings, get_ia_settings
from ia.exceptions import IAConfigurationError

_client = None
_client_config = None


def build_ia_client(config: IASettings | None = None):
    global _client, _client_config

    config = config or get_ia_settings()

    if _client is not None and _client_config == config:
        return _client

    if config.provider == "jan":
        _client = JanClient(config)
        _client_config = config
        return _client

    raise IAConfigurationError(f"Proveedor de IA no soportado: {config.provider}")
