# Partidas, torneos y métricas

## Propósito

[`match.py`](../src/arena/match.py) coordina objetos jugador compatibles con
`name` y `choose_move(game, player)`. Guarda cada movimiento, define el
resultado y permite resumir el desempeño por nombre.

## Flujo paso a paso

1. `play_match(player1, player2)` crea un `ConnectFour` y asigna el primer turno
   a `player1`.
2. En cada turno solicita una decisión al jugador activo y la aplica mediante
   `game.drop`.
3. Agrega un `MoveRecord` con la jugada, razón, intentos inválidos, fallback,
   latencia y tokens.
4. Si se pasó `on_move`, lo llama después de cada jugada con el registro y el
   juego actualizado.
5. Al terminar devuelve `MatchResult`, incluyendo ganador, registros y tablero
   final.
6. `run_tournament` crea nuevos jugadores para cada partida y alterna quién
   abre. `summarize` acumula estadísticas por nombre.

## API pública

| Elemento | Descripción |
| --- | --- |
| `MoveRecord` | Datos de una jugada completada. |
| `MatchResult` | Datos de una partida y propiedad `winner_name`. |
| `play_match(player1, player2, on_move)` | Ejecuta una partida. |
| `run_tournament(make_player_a, make_player_b, games, on_game)` | Ejecuta un torneo. |
| `summarize(results)` | Agrega métricas en un diccionario por jugador. |

Las métricas de `summarize` incluyen partidas, victorias, derrotas, empates,
jugadas, jugadas inválidas, fallbacks, latencia total y media, y tokens totales.
El promedio de latencia se calcula por jugada; si no hay jugadas, el divisor
protegido es uno.

## Ejemplo mínimo

```python
from arena.baseline import RandomPlayer
from arena.match import run_tournament, summarize

resultados = run_tournament(
    lambda: RandomPlayer(seed=1),
    lambda: RandomPlayer(seed=2),
    games=2,
)
print(summarize(resultados))
```

## Errores posibles

- `engine.InvalidMoveError` se propaga si un jugador propone una columna que el
  motor no puede aplicar.
- Los errores de los callbacks o de `choose_move` también se propagan; el
  orquestador no los oculta.
- El código no valida que los nombres de los jugadores sean únicos. Si dos
  jugadores comparten nombre, `summarize` los agrupa bajo la misma clave.
