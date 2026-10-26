# Definiciones declarativas: agentes y skills

## Propósito

[`skills.py`](../src/arena/skills.py) interpreta archivos Markdown que combinan
un frontmatter YAML con un cuerpo de instrucciones. Los archivos `.agent.md`
describen el modelo, opciones y skills; los `.skill.md` aportan instrucciones
reutilizables.

## Flujo paso a paso

1. `parse_frontmatter(text)` separa el bloque delimitado por `---` del cuerpo.
2. `load_agent(path)` valida `name` y `model`, y normaliza `options` y `skills`
   a los tipos esperados.
3. `load_skill(path)` valida `name`, `description`, `tipo` y el cuerpo de cada
   skill. Los tipos aceptados están en `SKILL_KINDS`: `personalidad` y
   `utilidad`.
4. `load_skill_library(root)` busca recursivamente `*.skill.md` y los indexa
   por nombre; los duplicados se consideran error.
5. `resolve_skills(config, library)` recupera las skills declaradas y conserva
   su orden.
6. `swap_personality(skills, personality)` reemplaza la personalidad existente
   o agrega la nueva al final, sin quitar skills de utilidad.

## API pública

| Elemento | Descripción |
| --- | --- |
| `Skill` | Datos inmutables de una skill cargada. |
| `AgentConfig` | Datos inmutables de un agente cargado. |
| `DefinitionError` | Error de valor para definiciones inválidas. |
| `parse_frontmatter(text)` | Devuelve metadatos YAML y cuerpo Markdown. |
| `load_skill(path)` | Carga y valida una skill. |
| `load_skill_library(root)` | Carga e indexa la biblioteca de skills. |
| `load_agent(path)` | Carga y valida un agente. |
| `resolve_skills(config, library)` | Resuelve los nombres declarados contra la biblioteca. |
| `swap_personality(skills, personality)` | Sustituye o agrega una personalidad. |

## Ejemplo mínimo

```python
from arena.skills import load_agent, load_skill_library, resolve_skills

config = load_agent("agents/jugador_llama.agent.md")
library = load_skill_library("skills")
skills = resolve_skills(config, library)
print(config.model, [skill.name for skill in skills])
```

## Errores posibles

- `DefinitionError` ante delimitadores ausentes, YAML inválido, metadatos que
  no sean un mapa, campos obligatorios faltantes, tipos incorrectos, skill sin
  instrucciones, nombres duplicados o referencias inexistentes.
- `OSError` si no se puede leer alguno de los archivos.
- La conversión YAML de campos no especificados como obligatorios conserva el
  comportamiento del parser: no se aplican validaciones adicionales a
  `description` ni a los valores individuales de `options`.
