"""Línea de comandos: ``python -m arena.cli play|tournament``."""

from __future__ import annotations

import argparse
import itertools
import json

from .factory import AGENTS_DIR, build_agent
from .match import play_match, run_tournament, summarize


def _make(args, side: str, seed: int | None = None):
    """Construye el agente configurado para uno de los lados del CLI.

    Args:
        args: Argumentos parseados por ``main``.
        side: Prefijo ``a`` o ``b`` de las opciones del agente.
        seed: Semilla opcional para las opciones del modelo.

    Returns:
        Agente construido con el archivo seleccionado, personalidad y ajustes.
    """
    path = AGENTS_DIR / f"jugador_{getattr(args, side)}.agent.md"
    personality = getattr(args, f"{side}_estilo")
    overrides = {}
    if args.temperature is not None:
        overrides["temperature"] = args.temperature
    if seed is not None:
        overrides["seed"] = seed
    return build_agent(path, personality=personality, option_overrides=overrides)


def main(argv: list[str] | None = None) -> None:
    """Interpreta argumentos y ejecuta una partida o torneo.

    Args:
        argv: Argumentos a interpretar; si es ``None``, usa los del proceso.

    Returns:
        ``None``. Imprime el resultado en la salida estándar.
    """
    parser = argparse.ArgumentParser(prog="arena")
    parser.add_argument("modo", choices=["play", "tournament"])
    parser.add_argument("--a", default="llama", help="agente 1: llama | qwen")
    parser.add_argument("--b", default="qwen", help="agente 2: llama | qwen")
    parser.add_argument("--a-estilo", default=None, help="skill de personalidad para A")
    parser.add_argument("--b-estilo", default=None, help="skill de personalidad para B")
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--games", type=int, default=4)
    args = parser.parse_args(argv)

    if args.modo == "play":
        result = play_match(
            _make(args, "a"), _make(args, "b"),
            on_move=lambda rec, game: print(
                f"[{rec.turn:02d}] {rec.name}: columna {rec.column + 1} "
                f"({rec.latency_s:.1f}s, inv={rec.invalid_attempts}) {rec.reason}"
            ),
        )
        print(result.final_board)
        print("Ganador:", result.winner_name or "empate")
    else:
        seeds = itertools.count(1)  # una semilla nueva en cada partida
        results = run_tournament(
            lambda: _make(args, "a", next(seeds)), lambda: _make(args, "b", next(seeds)), args.games,
            on_game=lambda i, r: print(f"Partida {i + 1}: {r.winner_name or 'empate'}"),
        )
        print(json.dumps(summarize(results), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
