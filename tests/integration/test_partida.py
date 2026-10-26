"""Pruebas de integración: agentes leídos desde los .md + orquestador + métricas + cliente HTTP.

Usan un Ollama falso para que sean rápidas y den siempre el mismo resultado.
La última prueba usa los modelos reales y solo corre con:  pytest -m ollama
"""

import json

import pytest
import requests

from arena.baseline import MinimaxPlayer
from arena.engine import ConnectFour
from arena.factory import build_agent
from arena.match import play_match, run_tournament, summarize
from arena.ollama_client import OllamaClient, OllamaError


def jugada(columna):
    """La respuesta que daría el modelo para jugar en una columna (1-7)."""
    return json.dumps({"columna": columna, "razon": "jugada de prueba"})


def test_una_partida_completa_termina_con_un_ganador(carpeta_agentes, cliente_falso):
    # Arrange: Llama apila la columna 1; Qwen juega 2, 3 y 4 sin bloquear
    llama = build_agent(carpeta_agentes / "jugador_llama.agent.md", client=cliente_falso([jugada(1)] * 4))
    qwen = build_agent(carpeta_agentes / "jugador_qwen.agent.md", client=cliente_falso([jugada(2), jugada(3), jugada(4)]))
    # Act
    resultado = play_match(llama, qwen)
    # Assert: Llama gana en vertical en la séptima jugada
    assert resultado.winner_name == llama.name
    assert len(resultado.records) == 7


def test_la_partida_sigue_aunque_el_modelo_responda_basura(carpeta_agentes, cliente_falso):
    # Arrange: la primera jugada de Llama son tres respuestas inválidas
    llama = build_agent(carpeta_agentes / "jugador_llama.agent.md",
                        client=cliente_falso(["no", "sé", "jugar"] + [jugada(1)] * 6))
    qwen = build_agent(carpeta_agentes / "jugador_qwen.agent.md", client=cliente_falso([jugada(7)] * 6))
    # Act
    resultado = play_match(llama, qwen)
    # Assert: la partida termina y queda registrado el fallback
    primera = resultado.records[0]
    assert primera.fallback is True
    assert primera.invalid_attempts == 3
    assert resultado.winner is not None


def test_cambiar_la_skill_cambia_el_prompt_que_recibe_el_modelo(carpeta_agentes, cliente_falso):
    # Arrange: el mismo agente, una vez agresivo y otra defensivo
    cliente_agresivo, cliente_defensivo = cliente_falso([jugada(4)]), cliente_falso([jugada(4)])
    agresivo = build_agent(carpeta_agentes / "jugador_llama.agent.md", personality="agresivo", client=cliente_agresivo)
    defensivo = build_agent(carpeta_agentes / "jugador_llama.agent.md", personality="defensivo", client=cliente_defensivo)
    # Act
    agresivo.choose_move(ConnectFour(), 1)
    defensivo.choose_move(ConnectFour(), 1)
    # Assert: cada modelo recibió solo las instrucciones de su personalidad
    prompt_agresivo = cliente_agresivo.consultas[0]["messages"][0]["content"]
    prompt_defensivo = cliente_defensivo.consultas[0]["messages"][0]["content"]
    assert "agresivo" in prompt_agresivo and "defensivo" not in prompt_agresivo
    assert "defensivo" in prompt_defensivo and "agresivo" not in prompt_defensivo


def test_los_parametros_cambiados_llegan_al_modelo(carpeta_agentes, cliente_falso):
    # Arrange: subimos la temperatura como se hace desde la interfaz
    cliente = cliente_falso([jugada(4)])
    agente = build_agent(carpeta_agentes / "jugador_llama.agent.md", option_overrides={"temperature": 1.2}, client=cliente)
    # Act
    agente.choose_move(ConnectFour(), 1)
    # Assert: cambia la temperatura y el resto queda como en el archivo
    parametros = cliente.consultas[0]["options"]
    assert parametros["temperature"] == 1.2
    assert parametros["num_ctx"] == 4096


def test_el_torneo_alterna_quien_empieza_y_calcula_metricas(carpeta_agentes, cliente_falso):
    # Arrange: Llama contra el rival de referencia (minimax)
    def crear_llama():
        return build_agent(carpeta_agentes / "jugador_llama.agent.md", client=cliente_falso([jugada(1)] * 30))
    # Act
    resultados = run_tournament(crear_llama, lambda: MinimaxPlayer(depth=3), games=2)
    metricas = summarize(resultados)
    # Assert: en la partida 1 abre Llama, en la 2 abre minimax
    assert resultados[0].names[1].startswith("JugadorLlama")
    assert resultados[1].names[1].startswith("Minimax")
    llama = next(valores for nombre, valores in metricas.items() if nombre.startswith("JugadorLlama"))
    assert llama["partidas"] == 2
    assert llama["victorias"] + llama["derrotas"] + llama["empates"] == 2


class SesionHttpFalsa:
    """Reemplaza a la librería requests: guarda el pedido y devuelve una respuesta armada."""

    def __init__(self, respuesta=None, error=None):
        self.respuesta, self.error, self.pedido = respuesta, error, None

    def post(self, url, json=None, timeout=None):
        if self.error:
            raise self.error
        self.pedido = (url, json)
        return self.respuesta


class RespuestaHttpFalsa:
    def __init__(self, datos, estado=200):
        self.datos, self.estado = datos, estado

    def raise_for_status(self):
        if self.estado >= 400:
            raise requests.HTTPError(str(self.estado))

    def json(self):
        return self.datos


def test_el_cliente_ollama_arma_bien_el_pedido():
    # Arrange
    sesion = SesionHttpFalsa(RespuestaHttpFalsa({"message": {"content": "{}"}, "prompt_eval_count": 12, "eval_count": 3}))
    cliente = OllamaClient("http://localhost:11434", session=sesion)
    # Act
    resultado = cliente.chat("qwen2.5:7b", [{"role": "user", "content": "hola"}], {"seed": 1})
    # Assert: va a /api/chat, sin streaming, pidiendo JSON, y se leen los tokens
    url, cuerpo = sesion.pedido
    assert url == "http://localhost:11434/api/chat"
    assert cuerpo["stream"] is False and cuerpo["format"] == "json"
    assert (resultado.prompt_tokens, resultado.completion_tokens) == (12, 3)


@pytest.mark.parametrize("sesion", [
    SesionHttpFalsa(error=requests.ConnectionError("Ollama apagado")),
    SesionHttpFalsa(RespuestaHttpFalsa({}, estado=500)),
    SesionHttpFalsa(RespuestaHttpFalsa({"sin": "mensaje"})),
])
def test_las_fallas_de_ollama_se_informan_como_ollama_error(sesion):
    # Act + Assert: apagado, error del servidor y respuesta incompleta
    with pytest.raises(OllamaError):
        OllamaClient(session=sesion).chat("qwen2.5:7b", [])


@pytest.mark.ollama
def test_partida_real_entre_llama_y_qwen(carpeta_agentes):
    """Necesita Ollama prendido y los dos modelos descargados."""
    # Arrange
    llama = build_agent(carpeta_agentes / "jugador_llama.agent.md", personality="agresivo")
    qwen = build_agent(carpeta_agentes / "jugador_qwen.agent.md", personality="defensivo")
    # Act
    resultado = play_match(llama, qwen)
    # Assert
    assert resultado.records
    assert resultado.winner in (1, 2, None)
