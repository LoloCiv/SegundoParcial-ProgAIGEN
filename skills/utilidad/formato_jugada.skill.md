---
name: formato_jugada
description: "Fija el contrato de salida: un único objeto JSON con la columna elegida y una razón breve."
tipo: utilidad
---

# Objetivo
Que la respuesta pueda ser leída por el orquestador sin ambigüedad.

# Entrada
Tablero en texto, columnas legales (numeradas 1-7) y amenazas inmediatas.

# Salida esperada
Un único objeto JSON, sin texto antes ni después:

```json
{"columna": 4, "razon": "bloqueo la diagonal del rival"}
```

# Restricciones
- `columna` es un entero entre 1 y 7 y debe figurar entre las columnas legales.
- `razon` es una sola frase de hasta 20 palabras.
- Nunca uses numeración 0-6.
