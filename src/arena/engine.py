"""Motor de Cuatro en Línea: solo reglas, no sabe nada de modelos de IA.

El tablero es una lista de 6 filas con 7 columnas. La fila 0 es la de arriba.
Los jugadores son 1 (ficha X) y 2 (ficha O). Dentro del motor las columnas van
de 0 a 6; a los modelos se las mostramos de 1 a 7 (esa conversión se hace en
``agent.py`` y ``parser.py``).
"""

ROWS = 6
COLS = 7
EMPTY = 0
SYMBOLS = {EMPTY: ".", 1: "X", 2: "O"}


class InvalidMoveError(ValueError):
    """La jugada rompe las reglas: columna inexistente, columna llena o partida terminada."""


def opponent_of(player: int) -> int:
    """Devuelve el identificador del rival.

    Args:
        player: Identificador del jugador; 1 corresponde a X y 2 a O.

    Returns:
        2 si ``player`` es 1; en cualquier otro caso, 1.
    """
    return 2 if player == 1 else 1


class ConnectFour:
    """Representa el estado mutable de una partida de Cuatro en Línea.

    El tablero tiene seis filas y siete columnas. Las columnas se indexan de
    0 a 6 y los jugadores se identifican con 1 y 2.
    """

    def __init__(self) -> None:
        """Inicializa un tablero vacío y asigna la apertura al jugador 1."""
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self.current_player = 1
        self.winner: int | None = None
        self.moves: list[int] = []  # columnas jugadas, en orden

    def copy(self) -> "ConnectFour":
        """Devuelve una copia independiente del estado actual.

        Returns:
            Una partida con el mismo tablero, turno, ganador y movimientos.
        """
        clone = ConnectFour()
        clone.grid = [row[:] for row in self.grid]
        clone.current_player = self.current_player
        clone.winner = self.winner
        clone.moves = self.moves[:]
        return clone

    @property
    def is_draw(self) -> bool:
        """Indica si el tablero está lleno y no hay ganador.

        Returns:
            ``True`` si la partida terminó en empate; si no, ``False``.
        """
        board_full = all(cell != EMPTY for cell in self.grid[0])
        return board_full and self.winner is None

    @property
    def is_over(self) -> bool:
        """Indica si hay un ganador o si la partida terminó en empate.

        Returns:
            ``True`` cuando la partida terminó.
        """
        return self.winner is not None or self.is_draw

    def legal_moves(self) -> list[int]:
        """Devuelve las columnas que todavía admiten una ficha.

        Returns:
            Índices de columna de 0 a 6; devuelve una lista vacía si hay ganador.
        """
        if self.winner is not None:
            return []
        return [column for column in range(COLS) if self.grid[0][column] == EMPTY]

    def drop(self, column: int) -> int:
        """Juega en una columna y actualiza el estado de la partida.

        Args:
            column: Índice de columna entre 0 y 6.

        Returns:
            Índice de la fila donde cayó la ficha.

        Raises:
            InvalidMoveError: Si la partida terminó, el índice no es un entero
                válido o la columna está llena.
        """
        if self.is_over:
            raise InvalidMoveError("la partida ya terminó")
        is_real_int = isinstance(column, int) and not isinstance(column, bool)
        if not is_real_int or not 0 <= column < COLS:
            raise InvalidMoveError(f"columna fuera de rango: {column!r}")
        if self.grid[0][column] != EMPTY:
            raise InvalidMoveError(f"la columna {column + 1} está llena")

        player = self.current_player
        row = self._place_piece(column, player)
        self.moves.append(column)
        if self._makes_four(row, column, player):
            self.winner = player
        else:
            self.current_player = opponent_of(player)
        return row

    def winning_moves(self, player: int) -> list[int]:
        """Busca jugadas que darían la victoria inmediata a un jugador.

        Args:
            player: Identificador del jugador que se evalúa.

        Returns:
            Índices de las columnas legales que formarían cuatro en línea.
        """
        winning_columns = []
        for column in self.legal_moves():
            test_game = self.copy()
            row = test_game._place_piece(column, player)
            if test_game._makes_four(row, column, player):
                winning_columns.append(column)
        return winning_columns

    def render(self) -> str:
        """Representa el tablero en texto con encabezado de columnas 1–7.

        Returns:
            Tablero de seis filas; las fichas se muestran como ``X``, ``O`` o
            ``.`` para las casillas vacías.
        """
        lines = [" ".join(str(column + 1) for column in range(COLS))]
        for row in self.grid:
            lines.append(" ".join(SYMBOLS[cell] for cell in row))
        return "\n".join(lines)

    def _place_piece(self, column: int, player: int) -> int:
        """Coloca una ficha en la casilla libre más baja de la columna.

        Args:
            column: Columna válida que todavía tiene espacio.
            player: Identificador del jugador que coloca la ficha.

        Returns:
            Índice de la fila en la que quedó la ficha.
        """
        for row in reversed(range(ROWS)):
            if self.grid[row][column] == EMPTY:
                self.grid[row][column] = player
                return row

    def _makes_four(self, row: int, column: int, player: int) -> bool:
        """Comprueba si una ficha recién colocada completa cuatro en línea.

        Args:
            row: Fila de la ficha evaluada.
            column: Columna de la ficha evaluada.
            player: Identificador del jugador dueño de la ficha.

        Returns:
            ``True`` si hay cuatro o más fichas consecutivas en alguna
            dirección; de lo contrario, ``False``.
        """
        # horizontal, vertical y las dos diagonales
        for step_row, step_col in ((0, 1), (1, 0), (1, 1), (1, -1)):
            in_line = 1  # la ficha recién puesta
            for direction in (1, -1):  # se cuenta hacia ambos lados
                r = row + direction * step_row
                c = column + direction * step_col
                while 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c] == player:
                    in_line += 1
                    r += direction * step_row
                    c += direction * step_col
            if in_line >= 4:
                return True
        return False
