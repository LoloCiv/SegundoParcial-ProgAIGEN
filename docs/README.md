# Documentación de Arena de Agentes

Arena de Agentes es un proyecto de Cuatro en Línea que permite ejecutar y
comparar jugadores respaldados por modelos locales de Ollama. Las instrucciones
de los agentes y sus estilos se declaran en archivos Markdown; el proyecto
incluye una interfaz Streamlit, una línea de comandos y jugadores de referencia
sin LLM.

## Requisitos y ejecución

Se requiere Python 3.11 o posterior. Desde la raíz del proyecto, instalá las
dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Para jugar con modelos LLM, instalá y ejecutá Ollama localmente y descargá los
modelos configurados en los archivos de `agents/` (por defecto, `llama3:latest`
y `qwen2.5:7b`).

Interfaz gráfica:

```powershell
streamlit run app.py
```

Línea de comandos:

```powershell
python arena_cli.py play --a llama --b qwen
python arena_cli.py tournament --games 4
```

Las pruebas unitarias y de integración simulada se ejecutan con:

```powershell
python -m pytest
```

La configuración de pytest excluye por defecto las pruebas marcadas `ollama`,
que requieren un servidor real y modelos descargados.

## Índice de documentación

### Guía del proyecto y diseño

- [Plan de documentación](./PLAN_DOCUMENTACION.md)
- [Especificación de diseño de Arena](./superpowers/specs/2026-10-24-arena-agentes-design.md)

### Código de `src/arena/`

- [Paquete y mapa de módulos](./arena.md)
- [Motor de Cuatro en Línea](./engine.md)
- [Parser de jugadas](./parser.md)
- [Definiciones declarativas: agentes y skills](./skills.md)
- [Cliente de Ollama](./ollama_client.md)
- [Agente respaldado por un modelo](./agent.md)
- [Jugadores de referencia](./baseline.md)
- [Partidas, torneos y métricas](./match.md)
- [Fábrica de agentes](./factory.md)
- [Interfaz de línea de comandos](./cli.md)

## Organización

`src/arena/` contiene las reglas, los agentes y la coordinación. Los perfiles
de agente viven en `agents/`; las instrucciones reutilizables, en `skills/`.
`app.py` presenta la interfaz Streamlit y `arena_cli.py` inicia la interfaz de
terminal.
