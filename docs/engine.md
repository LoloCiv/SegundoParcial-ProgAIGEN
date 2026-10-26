# Motor de Cuatro en Línea

## Propósito

[`engine.py`](../src/arena/engine.py) modela las reglas sin depender de Ollama,
del parser ni de la interfaz. El tablero es una matriz de seis filas por siete
columnas. Las filas se numeran internamente desde arriba; las columnas del
motor van de 0 a 6. El jugador 1 usa `X` y el 2 usa `O`.

## Flujo paso a paso

1. `ConnectFour()` crea un tablero vacío y asigna el primer turno al jugador 1.
2. `legal_moves()` devuelve las columnas cuya casilla superior está libre.
3. `drop(column)` deja caer la ficha actual hasta la fila libre más baja,
   registra el movimiento y comprueba si se formaron cuatro fichas.
4. Si no hubo victoria, cambia el turno. La partida termina cuando hay ganador
   o el tablero está lleno.
5. `copy()` permite simular posiciones sin modificar la partida original;
   `winning_moves()` usa copias para detectar victorias inmediatas.
6. `render()` genera una representación textual con encabezado de columnas de
   1 a 7.

## API pública

| Elemento | Descripción |
| --- | --- |
| `ConnectFour()` | Inicializa estado vacío. |
| `ConnectFour.copy()` | Devuelve una copia independiente. |
| `ConnectFour.is_draw` | Propiedad que indica empate. |
| `ConnectFour.is_over` | Propiedad que indica fin de partida. |
| `ConnectFour.legal_moves()` | Devuelve índices legales, de 0 a 6. |
| `ConnectFour.drop(column)` | Juega en una columna y devuelve la fila ocupada. |
| `ConnectFour.winning_moves(player)` | Devuelve columnas de victoria inmediata. |
| `ConnectFour.render()` | Devuelve el tablero como texto. |
| `opponent_of(player)` | Devuelve el identificador del rival. |
| `InvalidMoveError` | Error de valor para jugadas no permitidas. |

## Ejemplo mínimo

```python
from arena.engine import ConnectFour

partida = ConnectFour()
fila = partida.drop(3)  # El jugador 1 juega en la cuarta columna.
print(fila, partida.render())
```

## Errores posibles

`ConnectFour.drop` lanza `InvalidMoveError` si la partida ya terminó, si el
valor no es un entero válido en el rango 0–6 o si la columna está llena. La
clase valida que `bool` no se acepte como índice entero. Las funciones internas
`_place_piece` y `_makes_four` suponen que reciben una posición válida; no son
parte de la interfaz pública del motor.
