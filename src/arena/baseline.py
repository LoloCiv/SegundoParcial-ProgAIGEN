"""Rivales sin IA para medir a los agentes: uno al azar y uno con minimax."""

import random

from .agent import MoveDecision
from .engine import COLS, ConnectFour, opponent_of

CENTER_COLUMN = COLS // 2
# Se prueban primero las columnas del centro: mejora la poda del minimax
COLUMNS_CENTER_FIRST = sorted(range(COLS), key=lambda column: abs(column - CENTER_COLUMN))
WIN_SCORE = 10_000


class RandomPlayer:
    """Jugador de referencia que elige uniformemente entre jugadas legales."""

    def __init__(self, seed: int | None = None, name: str = "Aleatorio") -> None:
        """Configura el nombre visible y la semilla aleatoria.

        Args:
            seed: Semilla opcional para reproducir la secuencia de elecciones.
            name: Nombre del jugador en los resultados.
        """
        self.name = name
        self.random = random.Random(seed)

    def choose_move(self, game: ConnectFour, player: int) -> MoveDecision:
        """Elige al azar una de las columnas legales.

        Args:
            game: Estado actual de la partida.
            player: Identificador del jugador; no altera la estrategia aleatoria.

        Returns:
            Decisión con la columna elegida y la razón ``azar``.
        """
        return MoveDecision(self.random.choice(game.legal_moves()), "azar")


class MinimaxPlayer:
    """Jugador de referencia que evalúa posiciones con minimax y poda alpha-beta.

    La evaluación no terminal favorece las fichas en la columna central.
    Aumentar ``depth`` amplía la búsqueda y su costo computacional.
    """

    def __init__(self, depth: int = 4, name: str | None = None) -> None:
        """Configura la profundidad de búsqueda y el nombre visible.

        Args:
            depth: Cantidad de niveles buscados, incluido el movimiento inicial
                evaluado.
            name: Nombre opcional; si falta se genera uno con la profundidad.
        """
        self.depth = depth
        self.name = name or f"Minimax(p={depth})"

    def choose_move(self, game: ConnectFour, player: int) -> MoveDecision:
        """Evalúa cada columna legal y devuelve la de mayor puntaje minimax.

        Args:
            game: Estado actual de la partida.
            player: Identificador del jugador para quien se maximiza el puntaje.

        Returns:
            Decisión con la columna seleccionada y el puntaje calculado.
        """
        best_column, best_score = None, -WIN_SCORE * 10
        for column in COLUMNS_CENTER_FIRST:
            if column not in game.legal_moves():
                continue
            next_game = game.copy()
            next_game.drop(column)
            score = self._minimax(next_game, self.depth - 1, -WIN_SCORE * 10, WIN_SCORE * 10, player)
            if score > best_score:
                best_column, best_score = column, score
        return MoveDecision(best_column, f"minimax puntaje {best_score}")

    def _minimax(self, game: ConnectFour, depth: int, alpha: int, beta: int, me: int) -> int:
        """Calcula el puntaje minimax de una posición con poda alpha-beta.

        Args:
            game: Posición que se evalúa.
            depth: Niveles restantes de búsqueda.
            alpha: Mejor límite conocido para el jugador maximizador.
            beta: Mejor límite conocido para el jugador minimizador.
            me: Jugador desde cuya perspectiva se calcula el puntaje.

        Returns:
            Puntaje positivo favorable a ``me``, negativo favorable al rival o
            cero para empate; en la profundidad límite evalúa el centro.
        """
        if game.winner is not None:
            # Ganar antes vale más que ganar después (y perder después es mejor que perder ya)
            return WIN_SCORE + depth if game.winner == me else -WIN_SCORE - depth
        if game.is_draw:
            return 0
        if depth == 0:
            return self._score_center(game, me)

        my_turn = game.current_player == me
        best = -WIN_SCORE * 10 if my_turn else WIN_SCORE * 10
        for column in COLUMNS_CENTER_FIRST:
            if column not in game.legal_moves():
                continue
            next_game = game.copy()
            next_game.drop(column)
            score = self._minimax(next_game, depth - 1, alpha, beta, me)
            if my_turn:
                best = max(best, score)
                alpha = max(alpha, best)
            else:
                best = min(best, score)
                beta = min(beta, best)
            if alpha >= beta:
                break
        return best

    @staticmethod
    def _score_center(game: ConnectFour, me: int) -> int:
        """Evalúa la diferencia de fichas propias y rivales en el centro.

        Args:
            game: Posición sin resultado terminal que se evalúa.
            me: Jugador desde cuya perspectiva se calcula el puntaje.

        Returns:
            Tres veces la diferencia de fichas en la columna central.
        """
        center = [row[CENTER_COLUMN] for row in game.grid]
        return 3 * (center.count(me) - center.count(opponent_of(me)))
