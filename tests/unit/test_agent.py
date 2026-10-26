"""Pruebas unitarias del agente que decide la jugada (src/arena/agent.py)."""

import pytest

from arena.agent import LLMAgent, build_system_prompt
from arena.engine import ConnectFour
from arena.skills import load_agent, load_skill_library, resolve_skills


@pytest.fixture
def armar_agente(carpeta_agentes, carpeta_skills, cliente_falso):
    """Crea el agente de Llama conectado a un Ollama falso con las respuestas dadas."""
    def _armar(respuestas):
        config = load_agent(carpeta_agentes / "jugador_llama.agent.md")
        skills = resolve_skills(config, load_skill_library(carpeta_skills))
        cliente = cliente_falso(respuestas)
        return LLMAgent(config, skills, cliente, seed=1), cliente
    return _armar


def test_una_respuesta_valida_devuelve_la_columna(armar_agente):
    # Arrange
    agente, _ = armar_agente(['{"columna": 4, "razon": "centro"}'])
    # Act
    decision = agente.choose_move(ConnectFour(), 1)
    # Assert
    assert decision.column == 3
    assert decision.reason == "centro"
    assert decision.invalid_attempts == 0


def test_una_columna_llena_se_reintenta_mostrando_el_error(armar_agente):
    # Arrange: la columna 1 está llena y el modelo la elige primero
    partida = ConnectFour()
    for _ in range(6):
        partida.drop(0)
    agente, cliente = armar_agente(['{"columna": 1}', '{"columna": 2, "razon": "corrijo"}'])
    # Act
    decision = agente.choose_move(partida, partida.current_player)
    # Assert: juega la 2 y al modelo le llegó el motivo del error
    assert decision.column == 1
    assert decision.invalid_attempts == 1
    assert "no es legal" in cliente.consultas[1]["messages"][-1]["content"]


def test_tras_tres_respuestas_invalidas_juega_al_azar(armar_agente):
    # Arrange: el modelo contesta basura en el intento y en los dos reintentos
    agente, cliente = armar_agente(["basura", "basura", "basura"])
    partida = ConnectFour()
    # Act
    decision = agente.choose_move(partida, 1)
    # Assert: no se rompe, juega una columna legal y lo registra
    assert decision.fallback is True
    assert decision.column in partida.legal_moves()
    assert len(cliente.consultas) == 3


def test_el_prompt_incluye_el_rol_y_cada_skill(armar_agente):
    # Arrange
    agente, _ = armar_agente([])
    # Act
    prompt = build_system_prompt(agente.config, agente.skills)
    # Assert
    assert "Rol y propósito" in prompt
    for skill in agente.skills:
        assert f"## Skill: {skill.name}" in prompt
