"""Pruebas unitarias de la lectura de agentes y skills en Markdown (src/arena/skills.py)."""

import pytest

from arena.skills import DefinitionError, load_agent, load_skill, load_skill_library, resolve_skills, swap_personality


def test_lee_el_agente_con_modelo_parametros_y_skills(carpeta_agentes):
    # Arrange
    archivo = carpeta_agentes / "jugador_qwen.agent.md"
    # Act
    agente = load_agent(archivo)
    # Assert
    assert agente.model == "qwen2.5:7b"
    assert agente.options["temperature"] == 0.4
    assert agente.skills == ("formato_jugada", "analisis_amenazas", "equilibrado")


def test_carga_todas_las_skills_del_proyecto(carpeta_skills):
    # Act
    biblioteca = load_skill_library(carpeta_skills)
    # Assert
    assert set(biblioteca) == {"agresivo", "defensivo", "equilibrado", "formato_jugada", "analisis_amenazas"}
    assert biblioteca["agresivo"].kind == "personalidad"
    assert biblioteca["formato_jugada"].kind == "utilidad"


def test_una_skill_sin_tipo_lanza_error(tmp_path):
    # Arrange: un archivo de skill al que le falta el campo "tipo"
    archivo = tmp_path / "incompleta.skill.md"
    archivo.write_text("---\nname: incompleta\ndescription: sin tipo\n---\nInstrucciones", encoding="utf-8")
    # Act + Assert
    with pytest.raises(DefinitionError, match="tipo"):
        load_skill(archivo)


def test_cambiar_la_personalidad_reemplaza_solo_esa_skill(carpeta_agentes, carpeta_skills):
    # Arrange: el agente arranca con la personalidad "equilibrado"
    biblioteca = load_skill_library(carpeta_skills)
    skills = resolve_skills(load_agent(carpeta_agentes / "jugador_llama.agent.md"), biblioteca)
    # Act
    nuevas = swap_personality(skills, biblioteca["agresivo"])
    # Assert: entra "agresivo", sale "equilibrado" y las de utilidad quedan
    nombres = [skill.name for skill in nuevas]
    assert nombres == ["formato_jugada", "analisis_amenazas", "agresivo"]
