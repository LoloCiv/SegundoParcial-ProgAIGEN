---
name: analisis_amenazas
description: "Obliga a priorizar victorias y bloqueos inmediatos usando las listas calculadas por el sistema."
tipo: utilidad
---

# Objetivo
Evitar errores tácticos básicos: no dejar pasar una victoria propia ni una victoria rival.

# Entrada
Dos listas que calcula el sistema en cada turno: "columnas con las que ganás ahora mismo" y "columnas que bloquean una victoria inmediata del rival".

# Procedimiento
1. Si hay una columna con la que ganás ahora mismo, elegila.
2. Si no, y hay columnas que bloquean una victoria rival, elegí una de ellas.
3. Si no hay amenazas, decidí según tu personalidad.

# Restricciones
- No ignores nunca las listas del sistema: son correctas.
- La razón debe mencionar la amenaza cuando aplique el paso 1 o el 2.
