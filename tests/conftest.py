"""Piezas compartidas por todas las pruebas: un Ollama falso y las carpetas del proyecto."""

from pathlib import Path

import pytest

from arena.ollama_client import ChatResult

RAIZ = Path(__file__).resolve().parents[1]


class ClienteOllamaFalso:
    """Reemplaza a OllamaClient en las pruebas.

    Devuelve las respuestas que le programamos, en orden, y anota cada consulta
    que recibe para poder revisarla después. Así no hace falta un modelo real.
    """

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.consultas = []

    def chat(self, model, messages, options=None):
        self.consultas.append({"model": model, "messages": [dict(m) for m in messages], "options": options})
        texto = self.respuestas.pop(0) if self.respuestas else '{"columna": 4, "razon": "centro"}'
        return ChatResult(texto, latency_s=0.5, prompt_tokens=100, completion_tokens=10)


@pytest.fixture
def cliente_falso():
    """Devuelve la clase, para crear un cliente falso con las respuestas de cada test."""
    return ClienteOllamaFalso


@pytest.fixture
def carpeta_agentes():
    return RAIZ / "agents"


@pytest.fixture
def carpeta_skills():
    return RAIZ / "skills"
