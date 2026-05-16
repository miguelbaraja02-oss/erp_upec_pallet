import json

import requests
from requests import Response

from ia.clients.base import BaseIAClient
from ia.config import IASettings
from ia.exceptions import IAProviderError


class JanClient(BaseIAClient):
    """Client for Jan's local OpenAI-compatible API."""

    def __init__(self, config: IASettings):
        self.config = config
        self.base_url = config.jan_base_url.rstrip("/")
        self.model = config.jan_model
        self.timeout = config.request_timeout
        self.session = requests.Session()

    def chat(self, messages, **options):
        payload = self._build_chat_payload(messages, stream=False, **options)
        data = self._post("/chat/completions", payload)

        try:
            return self._message_content(data["choices"][0]["message"])
        except (KeyError, IndexError, TypeError) as exc:
            raise IAProviderError("Jan devolvio una respuesta inesperada.") from exc

    def generate_text(self, prompt, **options):
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **options)

    def stream_chat(self, messages, **options):
        payload = self._build_chat_payload(messages, stream=True, **options)

        try:
            with self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
                stream=True,
            ) as response:
                response.raise_for_status()
                response.encoding = "utf-8"
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data:"):
                        continue

                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break

                    chunk = self._loads_stream_chunk(data)
                    if chunk:
                        yield chunk
        except requests.HTTPError as exc:
            detail = self._response_error_detail(exc.response)
            raise IAProviderError(f"Error al consultar Jan local. {detail}") from exc
        except requests.RequestException as exc:
            raise IAProviderError("Error al consultar Jan local.") from exc

    def health_check(self):
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise IAProviderError("No se pudo conectar con Jan local.") from exc

        return True

    def _build_chat_payload(self, messages, stream=False, **options):
        payload = {
            "model": options.pop("model", self.model),
            "messages": messages,
            "max_tokens": options.pop("max_tokens", self.config.max_tokens),
        }

        if stream:
            payload["stream"] = True

        payload.update(self._extra_body())

        enable_thinking = options.pop("enable_thinking", self.config.enable_thinking)
        if enable_thinking:
            template_kwargs = payload.setdefault("chat_template_kwargs", {})
            template_kwargs["enable_thinking"] = True

        payload.update(options)
        return payload

    def _post(self, path, payload):
        try:
            response = self.session.post(
                f"{self.base_url}{path}",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = self._response_error_detail(exc.response)
            raise IAProviderError(f"Error al consultar Jan local. {detail}") from exc
        except requests.RequestException as exc:
            raise IAProviderError("Error al consultar Jan local.") from exc

        return self._json(response)

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.config.jan_api_key:
            headers["Authorization"] = f"Bearer {self.config.jan_api_key}"
        return headers

    def _json(self, response: Response):
        try:
            return response.json()
        except ValueError as exc:
            raise IAProviderError("Jan no devolvio JSON valido.") from exc

    def _response_error_detail(self, response: Response | None):
        if response is None:
            return "Sin detalle de respuesta."

        try:
            data = response.json()
        except ValueError:
            return response.text[:300]

        error = data.get("error")
        if isinstance(error, dict):
            message = error.get("message") or error
        else:
            message = data.get("message") or error or data
        return str(message)[:300]

    def _extra_body(self):
        try:
            extra_body = json.loads(self.config.jan_extra_body or "{}")
        except ValueError as exc:
            raise IAProviderError("IA_JAN_EXTRA_BODY debe ser JSON valido.") from exc

        if not isinstance(extra_body, dict):
            raise IAProviderError("IA_JAN_EXTRA_BODY debe ser un objeto JSON.")

        return extra_body.copy()

    def _message_content(self, message):
        content = message.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
                elif isinstance(item, str):
                    parts.append(item)
            return "".join(parts)
        return str(content)

    def _loads_stream_chunk(self, raw_data):
        try:
            data = json.loads(raw_data)
        except ValueError as exc:
            raise IAProviderError("Jan envio un fragmento JSON invalido.") from exc

        try:
            delta = data["choices"][0].get("delta", {})
            return delta.get("content", "")
        except (KeyError, IndexError, TypeError) as exc:
            raise IAProviderError("Jan devolvio un fragmento inesperado.") from exc
