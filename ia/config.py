import json
from dataclasses import dataclass
from urllib.parse import urlparse

from django.conf import settings

from ia.exceptions import IAConfigurationError


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


@dataclass(frozen=True)
class IASettings:
    provider: str
    local_only: bool
    jan_base_url: str
    jan_model: str
    jan_api_key: str
    jan_extra_body: str
    request_timeout: float
    max_tokens: int
    enable_thinking: bool


def get_ia_settings() -> IASettings:
    config = IASettings(
        provider=getattr(settings, "IA_PROVIDER", "jan"),
        local_only=getattr(settings, "IA_LOCAL_ONLY", True),
        jan_base_url=getattr(settings, "IA_JAN_BASE_URL", ""),
        jan_model=getattr(settings, "IA_JAN_MODEL", ""),
        jan_api_key=getattr(settings, "IA_JAN_API_KEY", ""),
        jan_extra_body=getattr(settings, "IA_JAN_EXTRA_BODY", "{}"),
        request_timeout=getattr(settings, "IA_REQUEST_TIMEOUT", 60),
        max_tokens=getattr(settings, "IA_MAX_TOKENS", 450),
        enable_thinking=getattr(settings, "IA_ENABLE_THINKING", False),
    )
    validate_ia_settings(config)
    return config


def validate_ia_settings(config: IASettings) -> None:
    if not config.provider:
        raise IAConfigurationError("IA_PROVIDER no esta configurado.")

    if config.provider != "jan":
        raise IAConfigurationError(f"Proveedor de IA no soportado: {config.provider}")

    if not config.jan_base_url:
        raise IAConfigurationError("IA_JAN_BASE_URL no esta configurado.")

    if not config.jan_model:
        raise IAConfigurationError("IA_JAN_MODEL no esta configurado.")

    parsed_url = urlparse(config.jan_base_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise IAConfigurationError("IA_JAN_BASE_URL debe ser una URL valida.")

    if config.local_only and parsed_url.hostname not in LOCAL_HOSTS:
        raise IAConfigurationError("IA_LOCAL_ONLY solo permite localhost o 127.0.0.1.")

    if config.max_tokens <= 0:
        raise IAConfigurationError("IA_MAX_TOKENS debe ser mayor que cero.")

    try:
        extra_body = json.loads(config.jan_extra_body or "{}")
    except json.JSONDecodeError as exc:
        raise IAConfigurationError("IA_JAN_EXTRA_BODY debe ser JSON valido.") from exc

    if not isinstance(extra_body, dict):
        raise IAConfigurationError("IA_JAN_EXTRA_BODY debe ser un objeto JSON.")
