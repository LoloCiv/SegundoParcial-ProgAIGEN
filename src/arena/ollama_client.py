"""Cliente mínimo de Ollama: manda la conversación a /api/chat y devuelve la respuesta."""

import time
from dataclasses import dataclass

import requests

DEFAULT_HOST = "http://localhost:11434"


class OllamaError(RuntimeError):
    """Ollama no respondió o respondió algo inesperado."""


@dataclass(frozen=True)
class ChatResult:
    """Respuesta de chat y métricas informadas por Ollama.

    Attributes:
        content: Texto devuelto por el modelo.
        latency_s: Duración de la consulta en segundos.
        prompt_tokens: Tokens de entrada informados por Ollama.
        completion_tokens: Tokens generados informados por Ollama.
    """

    content: str  # texto que devolvió el modelo
    latency_s: float  # segundos que tardó
    prompt_tokens: int  # tokens de entrada
    completion_tokens: int  # tokens generados


class OllamaClient:
    """Cliente HTTP para los endpoints de chat y listado de modelos de Ollama."""

    def __init__(self, host: str = DEFAULT_HOST, timeout: float = 180.0, session=None) -> None:
        """Configura el host, el tiempo límite y el transporte HTTP.

        Args:
            host: URL base del servidor Ollama.
            timeout: Tiempo máximo de espera para una consulta de chat.
            session: Objeto compatible con ``requests``; permite inyectar un
                transporte alternativo, por ejemplo en pruebas.
        """
        self.host = host.rstrip("/")
        self.timeout = timeout
        self.http = session or requests  # los tests pasan un doble de prueba

    def chat(self, model: str, messages: list[dict], options: dict | None = None) -> ChatResult:
        """Envía una conversación al endpoint ``/api/chat``.

        Args:
            model: Nombre del modelo de Ollama.
            messages: Mensajes de conversación con roles y contenido.
            options: Opciones del modelo, como ``temperature``, ``num_ctx`` o
                ``seed``.

        Returns:
            Respuesta del modelo y métricas disponibles.

        Raises:
            OllamaError: Si falla la solicitud HTTP, el JSON o la estructura
                esperada de la respuesta.
        """
        request_body = {
            "model": model,
            "messages": messages,
            "stream": False,  # una sola respuesta completa
            "format": "json",  # obliga al modelo a responder JSON
            "keep_alive": "10m",  # deja el modelo en memoria entre jugadas
            "options": options or {},
        }
        started_at = time.perf_counter()
        try:
            response = self.http.post(f"{self.host}/api/chat", json=request_body, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as error:
            raise OllamaError(f"falló la consulta a {model}: {error}") from error
        latency_s = time.perf_counter() - started_at

        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as error:
            raise OllamaError(f"respuesta inesperada de Ollama: {data!r}") from error

        return ChatResult(
            content=content,
            latency_s=latency_s,
            prompt_tokens=int(data.get("prompt_eval_count", 0)),
            completion_tokens=int(data.get("eval_count", 0)),
        )

    def list_models(self) -> list[str]:
        """Lista los nombres de modelos disponibles en Ollama.

        Returns:
            Nombres informados por el endpoint ``/api/tags``.

        Raises:
            OllamaError: Si no se puede consultar o interpretar la respuesta.
        """
        try:
            response = self.http.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            return [model["name"] for model in response.json()["models"]]
        except (requests.RequestException, ValueError, KeyError) as error:
            raise OllamaError(f"no se pudo listar modelos: {error}") from error
