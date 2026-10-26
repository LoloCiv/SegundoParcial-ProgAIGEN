# Plan de documentación

## Alcance y criterio

Documentar los diez módulos de `src/arena/` y el recorrido de uso del proyecto.
La documentación y los docstrings se redactarán en castellano rioplatense, sin
alterar la lógica. Los docstrings pendientes o breves se completarán en formato
PEP 257: resumen de una línea y, cuando corresponda, secciones `Args`, `Returns`
y `Raises`. No se atribuirán comportamientos que no estén implementados.

## Módulos de `src/arena/`

| Módulo | Qué hace |
| --- | --- |
| `__init__.py` | Identifica el paquete Arena de agentes que juegan Cuatro en Línea con skills declarativas. |
| `engine.py` | Implementa el tablero, las reglas, las jugadas legales y la detección de victorias y empates. |
| `parser.py` | Interpreta la respuesta del modelo y convierte la columna del JSON al índice que usa el motor. |
| `skills.py` | Lee y valida las definiciones Markdown con frontmatter YAML de agentes y skills. |
| `ollama_client.py` | Envía solicitudes al servidor local de Ollama y devuelve respuesta, latencia y uso de tokens. |
| `agent.py` | Construye prompts, solicita jugadas al modelo, valida respuestas y aplica reintentos y fallback. |
| `baseline.py` | Provee jugadores de referencia aleatorio y minimax para comparar agentes. |
| `match.py` | Orquesta partidas y torneos y calcula métricas por jugador. |
| `factory.py` | Construye agentes a partir de archivos declarativos, skills y ajustes opcionales. |
| `cli.py` | Expone los modos de partida y torneo desde la línea de comandos. |

## Docstrings pendientes o a mejorar

Se conservarán los resúmenes que ya sean correctos y se ampliarán cuando haga
falta para explicar parámetros, resultados y excepciones reales. Se revisarán
los siguientes puntos:

| Módulo | Docstrings que faltan | Docstrings existentes que conviene completar |
| --- | --- | --- |
| `__init__.py` | No hay funciones ni clases públicas sin documentar. | El docstring del módulo puede ampliarse para explicar el propósito del paquete y enlazar conceptualmente sus componentes principales. |
| `engine.py` | `ConnectFour`, `ConnectFour.__init__`, `ConnectFour.is_draw`, `ConnectFour.is_over`. | `opponent_of`, `copy`, `legal_moves`, `drop`, `winning_moves`, `render`, `_place_piece` y `_makes_four`: agregar `Args`, `Returns` y/o `Raises` según corresponda. Documentar que `drop` puede lanzar `InvalidMoveError` y qué estado representa cada propiedad. |
| `parser.py` | No faltan resúmenes. | `parse_move`: organizar la información existente en `Args`, `Returns` y `Raises`, incluyendo la conversión de columnas 1–7 a 0–6 y los errores ya descritos. |
| `skills.py` | `Skill`, `AgentConfig`, `load_skill`, `load_agent`. | `parse_frontmatter`, `load_skill_library`, `resolve_skills` y `swap_personality`: documentar argumentos, valores devueltos y `DefinitionError` cuando aplica. |
| `ollama_client.py` | `ChatResult`, `OllamaClient`, `OllamaClient.__init__`. | `chat` y `list_models`: sumar `Args`, `Returns` y `Raises`, incluyendo `OllamaError` y la información que devuelve cada método. |
| `agent.py` | `LLMAgent.__init__`, `LLMAgent.choose_move`. | `MoveDecision`, `build_system_prompt` y `build_turn_prompt`: precisar los datos que contienen/reciben y sus resultados. En `choose_move`, documentar intentos, métricas y fallback. |
| `baseline.py` | `RandomPlayer`, `RandomPlayer.__init__`, `RandomPlayer.choose_move`, `MinimaxPlayer.__init__`, `MinimaxPlayer.choose_move`. | `MinimaxPlayer`, `_minimax` y `_score_center`: completar parámetros y resultado; explicar profundidad y poda alpha-beta usando solo lo que implementa el código. |
| `match.py` | `MatchResult`, `MatchResult.winner_name`. | `MoveRecord`, `play_match`, `run_tournament` y `summarize`: completar `Args`, `Returns` y, cuando aplique, `Raises`; dejar claro el registro de jugadas, alternancia de apertura y métricas. |
| `factory.py` | `list_agent_files`, `list_personalities`. | `build_agent`: detallar entradas, configuración devuelta y errores que puede propagar durante la carga o selección de skills. |
| `cli.py` | `main`. | `_make`: documentar argumentos y agente construido. |

Al completar los docstrings también se verificará que cada nombre y excepción
mencionados exista en el código. No se cambiarán firmas ni lógica para ajustarlos.

## Archivos Markdown a generar y orden

1. `docs/README.md` — guía de entrada: propósito del proyecto, requisitos,
   ejecución de la interfaz Streamlit (`app.py`) y del lanzador CLI
   (`arena_cli.py`), configuración con archivos de `agents/` y `skills/`, y
   pruebas.
2. `docs/arena.md` — alcance del paquete `src/arena/` y mapa de sus módulos;
   corresponde a `src/arena/__init__.py`.
3. `docs/engine.md` — reglas y representación del tablero.
4. `docs/parser.md` — formato de respuesta esperado y conversión de columnas.
5. `docs/skills.md` — frontmatter, carga, validación y selección de skills.
6. `docs/ollama_client.md` — comunicación con Ollama y datos de respuesta.
7. `docs/agent.md` — construcción de prompts, elección de jugadas, reintentos y
   fallback.
8. `docs/baseline.md` — jugadores aleatorio y minimax como referencias.
9. `docs/match.md` — flujo de partidas, torneos, registros y resumen de métricas.
10. `docs/factory.md` — construcción y enumeración de agentes y personalidades.
11. `docs/cli.md` — argumentos y modos disponibles en la línea de comandos.

Los documentos de módulos incluirán propósito, flujo, tabla de funciones
públicas, ejemplo mínimo de uso y errores posibles. Los ejemplos se limitarán a
interfaces verificadas en el código y aclararán los requisitos externos que
necesiten.

## Analogía a desarrollar

Conviene explicar el ciclo de decisión de `LLMAgent.choose_move` como una
propuesta de jugada ante un árbitro: el modelo propone una columna, el parser y
el motor verifican que pueda jugarse y, si no, el agente devuelve el error como
retroalimentación para que el modelo corrija. El código permite hasta dos
reintentos después de la respuesta inicial; si ninguno produce una jugada
válida, el agente elige al azar una columna legal para que la partida continúe.
La analogía se incluirá principalmente en `docs/agent.md` y se resumirá en la
guía general.
