"""Arena de Agentes (Streamlit): partida en vivo y torneo Llama vs Qwen.

Ejecutar:  streamlit run app.py

Estructura de la pantalla:
  - Barra lateral: por cada jugador se elige el agente (.agent.md), la skill de
    personalidad y los parámetros del modelo (temperature, num_ctx).
  - Pestaña "Partida en vivo": juega una partida y dibuja el tablero jugada a jugada.
  - Pestaña "Torneo y métricas": juega varias partidas y muestra la tabla comparativa.
La lógica del juego y de los agentes vive en src/arena; este archivo solo dibuja.
"""

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from arena.engine import COLS, ROWS  # noqa: E402
from arena.factory import build_agent, list_agent_files, list_personalities  # noqa: E402
from arena.match import play_match, run_tournament, summarize  # noqa: E402
from arena.ollama_client import OllamaClient, OllamaError  # noqa: E402

st.set_page_config(page_title="Arena de Agentes", page_icon="🎮", layout="wide")

COLORS = {0: "#1e293b", 1: "#ef4444", 2: "#facc15"}


def board_html(grid) -> str:
    cells = "".join(
        f'<div style="width:46px;height:46px;border-radius:50%;background:{COLORS[cell]};margin:3px"></div>'
        for row in grid for cell in row
    )
    return (
        f'<div style="display:grid;grid-template-columns:repeat({COLS},52px);background:#2563eb;'
        f'padding:8px;border-radius:12px;width:fit-content">{cells}</div>'
    )


def player_panel(label: str, default_agent: int, default_style: str, key: str):
    st.subheader(label)
    files = list_agent_files()
    agent = st.selectbox("Agente (.agent.md)", files, index=default_agent, format_func=lambda p: p.name, key=f"{key}_a")
    styles = list_personalities()
    style = st.selectbox("Skill de personalidad", styles, index=styles.index(default_style), key=f"{key}_s")
    temperature = st.slider("temperature", 0.0, 1.5, 0.4, 0.1, key=f"{key}_t")
    num_ctx = st.select_slider("num_ctx", [1024, 2048, 4096, 8192], value=4096, key=f"{key}_c")
    return agent, style, {"temperature": temperature, "num_ctx": num_ctx}


def make_builder(cfg):
    """Devuelve una función que crea el agente; cada llamada usa una semilla nueva,
    así las partidas de un torneo no se repiten."""
    agent, style, overrides = cfg
    client = OllamaClient()
    seeds = itertools.count(1)
    return lambda: build_agent(agent, personality=style, option_overrides={**overrides, "seed": next(seeds)}, client=client)


with st.sidebar:
    st.title("🎮 Arena de Agentes")
    st.caption("Cuatro en Línea · Ollama local")
    cfg_a = player_panel("Jugador 1 (rojo)", 0, "agresivo", "p1")
    st.divider()
    cfg_b = player_panel("Jugador 2 (amarillo)", 1, "defensivo", "p2")
    try:
        st.success("Ollama: " + ", ".join(OllamaClient().list_models()) or "sin modelos")
    except OllamaError as exc:
        st.error(f"Ollama no responde: {exc}")

live_tab, tournament_tab = st.tabs(["Partida en vivo", "Torneo y métricas"])

with live_tab:
    if st.button("▶ Jugar partida", type="primary"):
        a, b = make_builder(cfg_a)(), make_builder(cfg_b)()
        st.write(f"**{a.name}** (rojo) vs **{b.name}** (amarillo)")
        board_slot, log_slot = st.empty(), st.empty()
        board_slot.markdown(board_html([[0] * COLS for _ in range(ROWS)]), unsafe_allow_html=True)
        lines = []

        def on_move(rec, game):
            board_slot.markdown(board_html(game.grid), unsafe_allow_html=True)
            flag = " ⚠️ fallback" if rec.fallback else ""
            lines.append(
                f"`{rec.turn:02d}` **{rec.name}** → col {rec.column + 1} · {rec.latency_s:.1f}s · "
                f"inválidas {rec.invalid_attempts}{flag} — _{rec.reason}_"
            )
            log_slot.markdown("\n\n".join(lines[-8:]))

        try:
            result = play_match(a, b, on_move=on_move)
            st.success(f"Ganador: {result.winner_name}" if result.winner else "Empate")
            st.dataframe(pd.DataFrame([r.__dict__ for r in result.records]), use_container_width=True)
        except OllamaError as exc:
            st.error(f"Error con Ollama: {exc}")

with tournament_tab:
    games = st.number_input("Partidas (se alterna quién abre)", 2, 40, 4, step=2)
    if st.button("🏆 Correr torneo"):
        progress = st.progress(0.0)
        try:
            results = run_tournament(
                make_builder(cfg_a), make_builder(cfg_b), int(games),
                on_game=lambda i, r: progress.progress((i + 1) / games, f"Partida {i + 1}: {r.winner_name or 'empate'}"),
            )
        except OllamaError as exc:
            st.error(f"Error con Ollama: {exc}")
        else:
            table = pd.DataFrame(summarize(results)).T
            st.dataframe(table, use_container_width=True)
            st.bar_chart(table[["victorias", "derrotas", "empates"]])
