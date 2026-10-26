"""Arma un ``LLMAgent`` a partir de su .agent.md, la biblioteca de skills y ajustes opcionales."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .agent import LLMAgent
from .ollama_client import OllamaClient
from .skills import load_agent, load_skill_library, resolve_skills, swap_personality

ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"


def build_agent(
    agent_path: str | Path,
    personality: str | None = None,
    option_overrides: dict | None = None,
    client: OllamaClient | None = None,
    skills_dir: str | Path = SKILLS_DIR,
    label: str | None = None,
) -> LLMAgent:
    """Construye un agente a partir de sus archivos declarativos.

    Args:
        agent_path: Ruta al archivo ``.agent.md``.
        personality: Nombre opcional de skill que reemplaza la personalidad
            declarada.
        option_overrides: Opciones que pisan las del archivo del agente.
        client: Cliente Ollama opcional; si falta se crea uno nuevo.
        skills_dir: Raíz de búsqueda de archivos ``.skill.md``.
        label: Nombre visible opcional para el agente.

    Returns:
        Agente configurado con las skills resueltas.

    Raises:
        DefinitionError: Si las definiciones están mal formadas o faltan skills
            declaradas.
        KeyError: Si no existe la personalidad solicitada.
        OSError: Si no se puede leer alguno de los archivos requeridos.
    """
    config = load_agent(agent_path)  # 1. leer el .agent.md
    library = load_skill_library(skills_dir)  # 2. leer todas las skills
    skills = resolve_skills(config, library)  # 3. quedarse con las que el agente declara
    if personality:  # 4. opcional: cambiar el estilo de juego sin tocar archivos
        if personality not in library:
            raise KeyError(f"no existe la skill '{personality}'")
        skills = swap_personality(skills, library[personality])
    if option_overrides:
        config = replace(config, options={**config.options, **option_overrides})
    return LLMAgent(config, skills, client or OllamaClient(), label=label)


def list_agent_files(agents_dir: str | Path = AGENTS_DIR) -> list[Path]:
    """Lista los archivos de agente de una carpeta.

    Args:
        agents_dir: Carpeta donde se buscan archivos ``*.agent.md``.

    Returns:
        Rutas encontradas en orden alfabético.
    """
    return sorted(Path(agents_dir).glob("*.agent.md"))


def list_personalities(skills_dir: str | Path = SKILLS_DIR) -> list[str]:
    """Lista los nombres de skills clasificadas como personalidad.

    Args:
        skills_dir: Carpeta raíz de búsqueda de skills.

    Returns:
        Nombres de personalidad en orden alfabético.

    Raises:
        DefinitionError: Si una skill encontrada no es válida o hay nombres
            duplicados.
        OSError: Si no se puede leer un archivo de skill.
    """
    return sorted(s.name for s in load_skill_library(skills_dir).values() if s.kind == "personalidad")
