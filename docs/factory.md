# Fábrica de agentes

## Propósito

[`factory.py`](../src/arena/factory.py) ensambla un `LLMAgent` a partir de un
archivo `.agent.md`, una biblioteca de skills y opciones de ejecución. También
expone las definiciones disponibles para que una interfaz pueda mostrarlas.

## Flujo paso a paso

1. `build_agent` carga la configuración del agente y la biblioteca de skills.
2. Resuelve las skills nombradas en el archivo.
3. Si se pidió una personalidad, comprueba que exista y reemplaza la actual.
4. Combina las opciones adicionales sobre las del archivo; los overrides tienen
   prioridad ante claves repetidas.
5. Construye `LLMAgent`, usando el cliente recibido o creando un `OllamaClient`.
6. `list_agent_files` y `list_personalities` enumeran archivos de agente y
   skills de tipo personalidad, respectivamente.

## API pública

| Elemento | Descripción |
| --- | --- |
| `build_agent(agent_path, personality, option_overrides, client, skills_dir, label)` | Carga y construye un agente. |
| `list_agent_files(agents_dir)` | Devuelve rutas a `*.agent.md`. |
| `list_personalities(skills_dir)` | Devuelve nombres de skills de personalidad. |

## Ejemplo mínimo

La construcción no consulta Ollama; la conexión se usa cuando el agente elige
una jugada:

```python
from arena.factory import build_agent, list_personalities

print(list_personalities())
agente = build_agent(
    "agents/jugador_llama.agent.md",
    personality="agresivo",
    option_overrides={"temperature": 0.2},
)
print(agente.name)
```

## Errores posibles

- `skills.DefinitionError` si una definición es inválida o el agente declara
  una skill inexistente.
- `KeyError` si la personalidad indicada no existe en la biblioteca cargada.
- `OSError` si no se puede leer un archivo.
- Un error de transporte o configuración puede aparecer más adelante cuando se
  use el agente para consultar Ollama; `build_agent` no hace esa consulta.
