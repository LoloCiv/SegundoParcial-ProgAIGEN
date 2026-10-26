"""Orquestador: juega una partida entre dos jugadores, un torneo, y calcula las métricas.

Un "jugador" es cualquier objeto con ``name`` y ``choose_move(game, player)``:
puede ser un ``LLMAgent`` o uno de ``baseline.py``.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from .engine import ConnectFour


@dataclass(frozen=True)
class MoveRecord:
    """Registro inmutable de una jugada y sus métricas asociadas.

    Attributes:
        turn: Número de turno, empezando en 1.
        player: Identificador del jugador (1 o 2).
        name: Nombre visible del jugador.
        column: Índice de columna del motor (0–6).
        reason: Explicación recibida en la decisión.
        invalid_attempts: Cantidad de respuestas inválidas anteriores.
        fallback: Indica si la decisión usó una columna aleatoria de respaldo.
        latency_s: Latencia acumulada de la decisión.
        prompt_tokens: Tokens de entrada acumulados.
        completion_tokens: Tokens generados acumulados.
    """

    turn: int
    player: int  # 1 o 2
    name: str
    column: int  # 0-6
    reason: str
    invalid_attempts: int
    fallback: bool
    latency_s: float
    prompt_tokens: int
    completion_tokens: int


@dataclass
class MatchResult:
    """Resultado de una partida y sus registros de movimientos.

    Attributes:
        names: Nombres asociados a los identificadores 1 y 2.
        winner: Identificador ganador o ``None`` si hubo empate.
        records: Jugadas realizadas en orden.
        final_board: Representación textual del tablero al terminar.
    """

    names: dict[int, str]  # {1: nombre del jugador 1, 2: nombre del jugador 2}
    winner: int | None  # 1, 2 o None si hubo empate
    records: list[MoveRecord] = field(default_factory=list)
    final_board: str = ""

    @property
    def winner_name(self) -> str | None:
        """Devuelve el nombre ganador o ``None`` si la partida terminó empatada.

        Returns:
            Nombre asociado a ``winner`` o ``None``.
        """
        return self.names[self.winner] if self.winner else None


def play_match(player1, player2, on_move: Callable[[MoveRecord, ConnectFour], None] | None = None) -> MatchResult:
    """Juega hasta que alguien gana o se llena el tablero. ``player1`` abre con X.

    Args:
        player1: Jugador con atributos ``name`` y ``choose_move(game, player)``.
        player2: Segundo jugador con la misma interfaz.
        on_move: Callback opcional invocado después de cada jugada con el
            registro y el estado actualizado.

    Returns:
        Resultado con ganador, registros y tablero final.

    Raises:
        InvalidMoveError: Si un jugador devuelve una columna que el motor no
            puede jugar.
    """
    game = ConnectFour()
    players = {1: player1, 2: player2}
    result = MatchResult(names={1: player1.name, 2: player2.name}, winner=None)

    while not game.is_over:
        player_number = game.current_player
        player = players[player_number]
        decision = player.choose_move(game, player_number)
        game.drop(decision.column)

        record = MoveRecord(
            turn=len(game.moves), player=player_number, name=player.name, column=decision.column,
            reason=decision.reason, invalid_attempts=decision.invalid_attempts, fallback=decision.fallback,
            latency_s=decision.latency_s, prompt_tokens=decision.prompt_tokens,
            completion_tokens=decision.completion_tokens,
        )
        result.records.append(record)
        if on_move:
            on_move(record, game)

    result.winner = game.winner
    result.final_board = game.render()
    return result


def run_tournament(make_player_a: Callable[[], object], make_player_b: Callable[[], object], games: int,
                   on_game: Callable[[int, MatchResult], None] | None = None) -> list[MatchResult]:
    """Ejecuta partidas alternando qué jugador abre.

    Args:
        make_player_a: Fábrica que crea el jugador A para cada partida.
        make_player_b: Fábrica que crea el jugador B para cada partida.
        games: Cantidad de partidas solicitadas.
        on_game: Callback opcional con índice desde cero y resultado al cerrar
            cada partida.

    Returns:
        Resultados de las partidas en orden. Un valor negativo de ``games``
        produce una lista vacía porque el rango no contiene iteraciones.
    """
    results = []
    for game_number in range(games):
        player_a, player_b = make_player_a(), make_player_b()
        a_opens = game_number % 2 == 0
        result = play_match(player_a, player_b) if a_opens else play_match(player_b, player_a)
        results.append(result)
        if on_game:
            on_game(game_number, result)
    return results


def summarize(results: list[MatchResult]) -> dict[str, dict[str, float]]:
    """Acumula resultados y métricas por nombre de jugador.

    Args:
        results: Resultados de partidas que se quieren resumir.

    Returns:
        Mapa de nombre a métricas: partidas, victorias, derrotas, empates,
        jugadas, jugadas inválidas, fallbacks, latencia total y media, y tokens.
        Si la entrada está vacía, devuelve un mapa vacío.
    """
    table: dict[str, dict[str, float]] = {}

    def stats_of(name: str) -> dict[str, float]:
        empty = dict.fromkeys(
            ("partidas", "victorias", "derrotas", "empates", "jugadas",
             "jugadas_invalidas", "fallbacks", "latencia_total_s", "tokens"), 0)
        return table.setdefault(name, empty)

    for result in results:
        for player_number, name in result.names.items():
            stats = stats_of(name)
            stats["partidas"] += 1
            if result.winner is None:
                stats["empates"] += 1
            elif result.winner == player_number:
                stats["victorias"] += 1
            else:
                stats["derrotas"] += 1

        for move in result.records:
            stats = stats_of(move.name)
            stats["jugadas"] += 1
            stats["jugadas_invalidas"] += move.invalid_attempts
            stats["fallbacks"] += int(move.fallback)
            stats["latencia_total_s"] += move.latency_s
            stats["tokens"] += move.prompt_tokens + move.completion_tokens

    for stats in table.values():
        stats["latencia_media_s"] = round(stats["latencia_total_s"] / max(stats["jugadas"], 1), 3)
    return table
