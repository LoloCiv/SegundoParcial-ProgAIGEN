# Paquete `arena`

## Propósito

`src/arena/` reúne la lógica de una arena de Cuatro en Línea: reglas
independientes de los modelos, agentes configurables con archivos Markdown,
conexión con Ollama y ejecución de partidas o torneos. La interfaz Streamlit y
el lanzador ejecutable están fuera del paquete, en `app.py` y `arena_cli.py`.

## Flujo general

1. `skills.py` carga agentes y skills desde Markdown con frontmatter YAML.
2. `factory.py` resuelve las skills y construye un `LLMAgent`.
3. `agent.py` prepara los prompts; `ollama_client.py` consulta al modelo y
   `parser.py` interpreta la columna elegida.
4. `engine.py` aplica las reglas del juego.
5. `match.py` coordina partidas y torneos; `baseline.py` ofrece rivales de
   referencia; `cli.py` expone una interfaz de terminal.

## Mapa de módulos

| Módulo | Responsabilidad |
| --- | --- |
| [`engine.py`](../src/arena/engine.py) | Tablero, reglas, jugadas legales, victorias y empates. |
| [`parser.py`](../src/arena/parser.py) | Conversión de la respuesta JSON del modelo a una columna del motor. |
| [`skills.py`](../src/arena/skills.py) | Carga y validación de agentes y skills declarativos. |
| [`ollama_client.py`](../src/arena/ollama_client.py) | Consultas HTTP a Ollama y métricas devueltas. |
| [`agent.py`](../src/arena/agent.py) | Prompts, validación, reintentos y fallback de un agente LLM. |
| [`baseline.py`](../src/arena/baseline.py) | Jugadores aleatorio y minimax. |
| [`match.py`](../src/arena/match.py) | Partidas, torneos y métricas agregadas. |
| [`factory.py`](../src/arena/factory.py) | Ensamblado de agentes desde las definiciones. |
| [`cli.py`](../src/arena/cli.py) | Modos `play` y `tournament` para terminal. |

## API pública

El paquete no define una API agregada en `__init__.py`; se importan los
componentes desde sus módulos.

| Elemento | Uso |
| --- | --- |
| `engine.ConnectFour` | Crear y modificar el tablero de una partida. |
| `factory.build_agent` | Construir un jugador de Ollama con definiciones declarativas. |
| `match.play_match` | Ejecutar una partida entre objetos jugador compatibles. |
| `match.run_tournament` | Ejecutar varias partidas alternando quién abre. |
| `match.summarize` | Agregar métricas de los resultados. |

## Ejemplo mínimo

Este ejemplo juega una partida entre dos jugadores aleatorios sin requerir un
servidor de Ollama:

```python
from arena.baseline import RandomPlayer
from arena.match import play_match

resultado = play_match(RandomPlayer(seed=1), RandomPlayer(seed=2))
print(resultado.winner_name or "empate")
print(resultado.final_board)
```

Con `pyproject.toml` instalado o configurando `PYTHONPATH=src`, el paquete se
importa como `arena`.

## Errores posibles

- `engine.InvalidMoveError`: una jugada no respeta las reglas.
- `parser.MoveParseError`: la respuesta del modelo no contiene una jugada
  interpretable.
- `skills.DefinitionError`: una definición declarativa está incompleta,
  malformada o referencia una skill inexistente.
- `ollama_client.OllamaError`: falla la consulta a Ollama o su respuesta no
  tiene la estructura esperada.
- También pueden propagarse errores de lectura de archivos (`OSError`) o de
  configuración según el componente utilizado.
