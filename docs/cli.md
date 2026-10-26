# Interfaz de línea de comandos

## Propósito

[`cli.py`](../src/arena/cli.py) ofrece los modos `play` y `tournament`. Se puede
invocar como módulo (`python -m arena.cli`) o mediante el lanzador
[`arena_cli.py`](../arena_cli.py), que agrega `src` a la ruta de importación.

## Flujo paso a paso

1. `main(argv)` define y parsea los argumentos.
2. `_make(args, side, seed)` localiza el archivo del agente (`llama` o `qwen`),
   lee la personalidad seleccionada y arma los overrides de temperatura y
   semilla.
3. En modo `play`, ejecuta una partida e imprime cada movimiento, tablero,
   ganador o empate.
4. En modo `tournament`, asigna una semilla nueva por partida, ejecuta el
   número solicitado y serializa `summarize(results)` como JSON.

## Argumentos

| Argumento | Valor por defecto | Descripción |
| --- | --- | --- |
| `modo` | Obligatorio: `play` o `tournament` | Operación a ejecutar. |
| `--a` | `llama` | Agente del lado A: `llama` o `qwen`. |
| `--b` | `qwen` | Agente del lado B: `llama` o `qwen`. |
| `--a-estilo` | `None` | Skill de personalidad para A. |
| `--b-estilo` | `None` | Skill de personalidad para B. |
| `--temperature` | `None` | Override de temperatura aplicado a ambos agentes. |
| `--games` | `4` | Cantidad de partidas en un torneo. |

## API pública

| Elemento | Descripción |
| --- | --- |
| `main(argv=None)` | Parsea argumentos y ejecuta el modo solicitado. |

## Ejemplo mínimo

Con el paquete importable desde `src` y un servidor Ollama disponible:

```powershell
python arena_cli.py play --a llama --b qwen
python arena_cli.py tournament --games 4 --temperature 0.4
```

También se puede llamar a `main` desde Python pasando argumentos explícitos:

```python
from arena.cli import main

main(["play", "--a", "llama", "--b", "qwen"])
```

## Errores posibles

- `argparse` muestra un error de uso si `modo` o alguna opción no cumple el
  formato esperado.
- La carga de los agentes puede propagar `DefinitionError`, `KeyError` u
  `OSError`, según las definiciones presentes.
- Los errores de Ollama durante una partida se propagan desde `main`; el CLI no
  los convierte en un resultado exitoso.
