# Parser de jugadas

## Propósito

[`parser.py`](../src/arena/parser.py) convierte la respuesta textual de un
modelo en una jugada que pueda consumir el motor. La convención externa usa
columnas de 1 a 7; el motor usa índices de 0 a 6.

## Flujo paso a paso

1. `parse_move(text)` busca el primer objeto delimitado por llaves en el texto,
   así que puede tolerar texto antes o después del JSON.
2. Decodifica el objeto JSON y exige que sea un mapa con la clave `columna`.
3. Convierte el valor de `columna` a entero y verifica el rango 1–7.
4. Resta uno para devolver el índice de columna del motor. Si falta `razon`,
   devuelve una cadena vacía; si existe, la convierte a texto.

Formato esperado:

```json
{"columna": 4, "razon": "ocupo el centro"}
```

## API pública

| Elemento | Descripción |
| --- | --- |
| `parse_move(text)` | Devuelve `(columna_0_a_6, razon)`. |
| `MoveParseError` | Error de valor para respuestas que no representan una jugada válida. |

## Ejemplo mínimo

```python
from arena.parser import parse_move

columna, razon = parse_move('{"columna": "4", "razon": "centro"}')
assert columna == 3
```

## Errores posibles

`parse_move` lanza `MoveParseError` si el contenido no es texto, no contiene
un objeto JSON, el JSON es inválido, falta `columna`, el valor no se puede
convertir a entero o queda fuera del rango 1–7. La función valida el formato y
el rango, pero no conoce el estado del tablero; por eso una columna llena se
rechaza después, al validar la jugada contra el motor.
