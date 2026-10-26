# Arena de Agentes: Llama vs Qwen en Cuatro en Línea

Segundo parcial de Programación con IA Generativa. Dos agentes que corren **localmente con Ollama**, uno Llama y otro Qwen, juegan Cuatro en Línea entre sí. Su comportamiento (agresivo, defensivo, equilibrado) se define con **skills en Markdown** intercambiables, y el modelo se afina con parámetros de muestreo declarados en cada `.agent.md`. El proyecto mide qué modelo y qué estilo rinden mejor.

Es la evolución del Parcial 1 (una persona contra un agente vía MCP): ahora juegan agente contra agente, sin intervención humana.

## Arquitectura

```
agents/*.agent.md ───┐                       ┌─> engine.py   (reglas, victoria, amenazas)
                     ├─> factory ─> LLMAgent ┤
skills/**/*.skill.md ┘               │       └─> parser.py   (JSON del modelo -> columna)
                                     └──────> ollama_client.py ──HTTP──> Ollama (localhost:11434)

match.py: orquesta la partida, registra cada jugada y calcula métricas (torneo)
app.py:   interfaz Streamlit    ·    arena_cli.py: línea de comandos
```

- **Agente** (`agents/`): frontmatter YAML con `name`, `model`, `options` (temperature, num_ctx, num_predict, top_p, seed) y `skills`. Los dos agentes son idénticos salvo el modelo.
- **Skill** (`skills/`): rol, objetivo, entradas, salidas y restricciones. Dos tipos: `personalidad` (cómo juega) y `utilidad` (formato de salida y análisis de amenazas).
- **El código decide qué es legal; el modelo decide qué conviene.** Una jugada ilegal o mal formada se reintenta hasta 2 veces, mostrándole el error al modelo. Si sigue fallando, se juega una columna legal al azar y se registra como `fallback`.

## Requisitos

- Python 3.11 o posterior
- [Ollama](https://ollama.com/download) (en Windows: `irm https://ollama.com/install.ps1 | iex`)
- GPU recomendada: cada modelo de 7-8B usa unos 5 GB de memoria de video

## Puesta en marcha

```powershell
# 1. Modelos (una sola vez)
ollama pull llama3
ollama pull qwen2.5:7b

# 2. Entorno de Python
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Interfaz
streamlit run app.py
```

## Uso desde la terminal

```powershell
# Una partida con estilos distintos
python arena_cli.py play --a llama --b qwen --a-estilo agresivo --b-estilo defensivo

# Torneo de 6 partidas (se alterna quién abre) con métricas en JSON
python arena_cli.py tournament --a llama --b qwen --games 6

# Cambiar un parámetro del modelo sin tocar archivos
python arena_cli.py play --temperature 1.0
```

## Cómo cambiar el comportamiento

| Quiero... | Hago... |
|---|---|
| Que un agente sea más agresivo | Elegir la skill `agresivo` en la interfaz, usar `--a-estilo agresivo`, o cambiarla en el `skills:` de su `.agent.md` |
| Crear un estilo nuevo | Copiar un `.skill.md` de `skills/personalidad/` y editar el texto |
| Hacerlo más o menos creativo | Cambiar `temperature` en el `.agent.md` o en el control de la interfaz |
| Probar otro modelo | Cambiar `model:` en el `.agent.md` (con un `ollama pull` previo) |

## Pruebas

```powershell
pytest            # pruebas unitarias y de integración, con un Ollama simulado
pytest -v         # lo mismo, mostrando el nombre de cada prueba
pytest -m ollama  # además, una partida real (requiere Ollama y los modelos)
```

- `tests/unit/`: el motor del juego, el intérprete de respuestas, la lectura de agentes y skills, y la lógica del agente (reintentos y fallback). Patrón AAA, casos borde y excepciones.
- `tests/integration/test_partida.py`: agentes leídos desde sus `.md` + orquestador + métricas + cliente HTTP, con dobles de prueba de Ollama y de `requests`.
- `tests/conftest.py`: el `ClienteOllamaFalso` y las rutas compartidas por todas las pruebas.

## Resultados de referencia

Torneo de 6 partidas, Llama 3 (agresivo) contra Qwen 2.5 (defensivo): Qwen ganó 5 y Llama 1, sin diferencias de velocidad (unos 2,6 s por jugada). Con los estilos invertidos, Qwen también ganó todas las partidas de prueba: en este juego pesa más el modelo que la personalidad.

## Documentación

- [`docs/README.md`](docs/README.md): índice de la documentación técnica de cada módulo, generada con el agente `Documentador`.
- [`docs/PLAN_DOCUMENTACION.md`](docs/PLAN_DOCUMENTACION.md): el plan que siguió el agente antes de documentar.
- [`.github/agents/documentador.agent.md`](.github/agents/documentador.agent.md): la definición de ese agente.
- [`docs/GUION_VIDEO.md`](docs/GUION_VIDEO.md): el guion del video de presentación.

## Estructura

```
agents/        agentes declarativos (.agent.md)
skills/        skills de personalidad y de utilidad (.skill.md)
src/arena/     motor, intérprete, agente, cliente de Ollama, orquestador y CLI
tests/         pruebas unitarias y de integración
docs/          documentación técnica, guion y carátulas del video
app.py         interfaz Streamlit
arena_cli.py   lanzador de la línea de comandos
```
