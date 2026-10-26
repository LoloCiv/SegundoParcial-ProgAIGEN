# Jugadores de referencia

## Propósito

[`baseline.py`](../src/arena/baseline.py) contiene dos jugadores que no
consultan un modelo de lenguaje. Sirven para ejecutar partidas reproducibles o
como rivales de comparación: uno elige al azar y otro busca posiciones con
minimax.

## Flujo paso a paso

1. `RandomPlayer.choose_move` obtiene `game.legal_moves()` y elige una columna
   con su generador aleatorio.
2. `MinimaxPlayer.choose_move` prueba las columnas legales empezando por el
   centro.
3. Para cada jugada simula una copia del tablero y busca recursivamente hasta
   la profundidad configurada.
4. `_minimax` maximiza en turnos propios y minimiza en los del rival; los
   límites alpha y beta permiten podar ramas que no pueden mejorar el resultado.
5. En el límite de profundidad sin resultado terminal, `_score_center` puntúa
   la diferencia de fichas en la columna central.

## API pública

| Elemento | Descripción |
| --- | --- |
| `RandomPlayer(seed, name)` | Jugador aleatorio con semilla opcional. |
| `RandomPlayer.choose_move(game, player)` | Devuelve una columna legal elegida al azar. |
| `MinimaxPlayer(depth, name)` | Jugador de búsqueda con profundidad configurable. |
| `MinimaxPlayer.choose_move(game, player)` | Devuelve la mejor columna encontrada por minimax. |

## Ejemplo mínimo

```python
from arena.baseline import MinimaxPlayer, RandomPlayer
from arena.match import play_match

resultado = play_match(MinimaxPlayer(depth=2), RandomPlayer(seed=7))
print(resultado.winner_name or "empate")
```

## Errores posibles

Los jugadores asumen que se los consulta durante una partida con al menos una
columna legal. No definen una excepción propia: un estado sin jugadas puede
provocar un error al elegir de una lista vacía; normalmente el orquestador no
los consulta después del final de la partida.
