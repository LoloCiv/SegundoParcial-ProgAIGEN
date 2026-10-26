# Agente respaldado por un modelo

## Propósito

[`agent.py`](../src/arena/agent.py) adapta un modelo de Ollama al contrato de
jugador de la arena. Combina las instrucciones del `.agent.md` con las skills,
describe la posición actual y convierte la respuesta del modelo en una decisión
medible.

## Flujo paso a paso

1. `build_system_prompt` concatena el cuerpo del agente con las skills recibidas,
   respetando el orden.
2. `build_turn_prompt` incluye el tablero, el jugador actual, columnas legales,
   victorias inmediatas propias y columnas para bloquear al rival.
3. `LLMAgent.choose_move` envía ambos mensajes a Ollama y acumula latencia y
   tokens.
4. `parse_move` interpreta el JSON; el agente verifica además que la columna
   esté entre las legales del estado actual.
5. Ante una respuesta inválida, agrega la respuesta y el error a la
   conversación. Hace hasta dos reintentos después del primer intento.
6. Si todos los intentos fallan, elige una columna legal aleatoria y marca
   `fallback=True`. El resultado queda en `MoveDecision`.

## API pública

| Elemento | Descripción |
| --- | --- |
| `MoveDecision` | Jugada elegida, razón, fallback y métricas acumuladas. |
| `build_system_prompt(config, skills)` | Arma el prompt de sistema. |
| `build_turn_prompt(game, player)` | Describe el turno para el modelo. |
| `LLMAgent(config, skills, client, label, seed)` | Configura el jugador Ollama. |
| `LLMAgent.choose_move(game, player)` | Solicita y valida una decisión de jugada. |

## Ejemplo mínimo

La construcción carga los archivos declarativos y luego la partida consulta
Ollama; por eso este ejemplo requiere un servidor activo y el modelo indicado
por el archivo:

```python
from arena.factory import build_agent
from arena.engine import ConnectFour

agente = build_agent("agents/jugador_llama.agent.md")
decision = agente.choose_move(ConnectFour(), player=1)
print(decision.column, decision.reason)
```

## Errores posibles

- `OllamaError` se propaga si falla el cliente.
- `MoveParseError` se captura durante la validación: se registra como intento
  inválido y no sale del método mientras queden reintentos.
- La columna puede estar dentro del rango del parser pero ser ilegal porque la
  columna está llena; también se trata como intento inválido.
- El fallback requiere que exista al menos una columna legal. En el flujo
  normal, `match.play_match` solo solicita jugadas mientras la partida no haya
  terminado.

## Analogía: propuesta y árbitro

Pensá al modelo como alguien que propone una columna y al parser junto con el
motor como el árbitro: revisan que la propuesta tenga formato entendible y que
la columna se pueda jugar. Si hay un error, el agente se lo comunica al modelo
para que corrija; tras dos reintentos, una elección aleatoria legal permite que
la partida siga sin quedar trabada.
