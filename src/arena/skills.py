"""Carga de agentes y skills declarativos (Markdown con frontmatter YAML).

Un archivo .md se lee en dos partes:
  - el bloque entre '---' (frontmatter YAML): datos como name, model, options, skills;
  - el resto (cuerpo Markdown): las instrucciones que se le pasan al modelo.

Un agente (``AgentConfig``) nombra las skills que usa; la biblioteca de skills
(``load_skill_library``) las busca por nombre en la carpeta ``skills/``.
Si un archivo está mal formado se lanza ``DefinitionError`` con un mensaje claro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

SKILL_KINDS = ("personalidad", "utilidad")


class DefinitionError(ValueError):
    """Un archivo .agent.md o .skill.md está mal formado."""


@dataclass(frozen=True)
class Skill:
    """Definición cargada de una skill declarativa.

    Attributes:
        name: Nombre usado para referenciar la skill.
        description: Descripción indicada en el frontmatter.
        kind: Tipo de skill, por ejemplo ``personalidad`` o ``utilidad``.
        body: Instrucciones Markdown que recibe el agente.
        path: Ruta del archivo de origen, si está disponible.
    """

    name: str
    description: str
    kind: str
    body: str
    path: Path | None = None


@dataclass(frozen=True)
class AgentConfig:
    """Configuración declarativa de un agente cargado desde Markdown.

    Attributes:
        name: Nombre del agente.
        description: Descripción declarativa, vacía si no se indicó.
        model: Nombre del modelo que consultará el agente.
        options: Opciones que se envían a Ollama.
        skills: Nombres de skills declarados y conservados en orden.
        body: Instrucciones Markdown del agente.
        path: Ruta del archivo de origen, si está disponible.
    """

    name: str
    description: str
    model: str
    options: dict = field(default_factory=dict)
    skills: tuple[str, ...] = ()
    body: str = ""
    path: Path | None = None


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Separa los metadatos YAML del cuerpo Markdown.

    Args:
        text: Contenido completo del archivo declarativo.

    Returns:
        Tupla con el mapa de metadatos y el cuerpo sin espacios exteriores.

    Raises:
        DefinitionError: Si faltan delimitadores, el YAML es inválido o no
            representa un mapa.
    """
    stripped = text.lstrip("﻿")
    if not stripped.startswith("---"):
        raise DefinitionError("falta el frontmatter YAML (debe empezar con '---')")
    parts = stripped.split("---", 2)
    if len(parts) < 3:
        raise DefinitionError("frontmatter sin cierre '---'")
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        raise DefinitionError(f"YAML inválido: {exc}") from exc
    if not isinstance(meta, dict):
        raise DefinitionError("el frontmatter debe ser un mapa clave: valor")
    return meta, parts[2].strip()


def load_skill(path: str | Path) -> Skill:
    """Carga y valida una definición de skill.

    Args:
        path: Ruta al archivo Markdown de la skill.

    Returns:
        Skill con los metadatos y las instrucciones del archivo.

    Raises:
        DefinitionError: Si el frontmatter o los campos obligatorios son
            inválidos, el tipo no está admitido o el cuerpo está vacío.
        OSError: Si no se puede leer el archivo.
    """
    path = Path(path)
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    for key in ("name", "description", "tipo"):
        if not meta.get(key):
            raise DefinitionError(f"{path.name}: falta el campo '{key}'")
    if meta["tipo"] not in SKILL_KINDS:
        raise DefinitionError(f"{path.name}: tipo debe ser uno de {SKILL_KINDS}")
    if not body:
        raise DefinitionError(f"{path.name}: la skill no tiene instrucciones")
    return Skill(meta["name"], meta["description"], meta["tipo"], body, path)


def load_skill_library(root: str | Path) -> dict[str, Skill]:
    """Carga las skills encontradas bajo una carpeta y las indexa por nombre.

    Args:
        root: Carpeta en la que se buscan recursivamente archivos
            ``*.skill.md``.

    Returns:
        Mapa cuyo índice es el nombre de cada skill cargada.

    Raises:
        DefinitionError: Si alguna skill no es válida o hay nombres duplicados.
        OSError: Si no se puede leer un archivo encontrado.
    """
    library: dict[str, Skill] = {}
    for path in sorted(Path(root).rglob("*.skill.md")):
        skill = load_skill(path)
        if skill.name in library:
            raise DefinitionError(f"skill duplicada: {skill.name}")
        library[skill.name] = skill
    return library


def load_agent(path: str | Path) -> AgentConfig:
    """Carga y valida la configuración declarativa de un agente.

    Args:
        path: Ruta al archivo Markdown del agente.

    Returns:
        Configuración con metadatos, opciones, skills y cuerpo.

    Raises:
        DefinitionError: Si faltan campos obligatorios o ``options`` y
            ``skills`` tienen tipos no admitidos.
        OSError: Si no se puede leer el archivo.
    """
    path = Path(path)
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    for key in ("name", "model"):
        if not meta.get(key):
            raise DefinitionError(f"{path.name}: falta el campo '{key}'")
    options = meta.get("options") or {}
    if not isinstance(options, dict):
        raise DefinitionError(f"{path.name}: 'options' debe ser un mapa")
    skills = meta.get("skills") or []
    if not isinstance(skills, list):
        raise DefinitionError(f"{path.name}: 'skills' debe ser una lista")
    return AgentConfig(
        name=meta["name"],
        description=meta.get("description", ""),
        model=meta["model"],
        options=options,
        skills=tuple(str(s) for s in skills),
        body=body,
        path=path,
    )


def resolve_skills(config: AgentConfig, library: dict[str, Skill]) -> list[Skill]:
    """Resuelve los nombres declarados por un agente contra una biblioteca.

    Args:
        config: Configuración que contiene los nombres de skills requeridos.
        library: Skills disponibles indexadas por nombre.

    Returns:
        Skills correspondientes, en el orden declarado por el agente.

    Raises:
        DefinitionError: Si falta una o más skills solicitadas.
    """
    missing = [name for name in config.skills if name not in library]
    if missing:
        raise DefinitionError(f"{config.name}: skills inexistentes: {', '.join(missing)}")
    return [library[name] for name in config.skills]


def swap_personality(skills: list[Skill], personality: Skill) -> list[Skill]:
    """Reemplaza la personalidad actual o agrega una nueva a la lista.

    Args:
        skills: Skills existentes del agente.
        personality: Skill de personalidad que se quiere usar.

    Returns:
        Nueva lista con las skills no personales originales y la personalidad
        indicada al final.

    Raises:
        DefinitionError: Si ``personality`` no es de tipo ``personalidad``.
    """
    if personality.kind != "personalidad":
        raise DefinitionError(f"{personality.name} no es una skill de personalidad")
    result = [s for s in skills if s.kind != "personalidad"]
    result.append(personality)
    return result
