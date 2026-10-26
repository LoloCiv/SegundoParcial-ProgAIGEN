"""Pruebas unitarias del motor del juego (src/arena/engine.py)."""

import pytest

from arena.engine import COLS, ROWS, ConnectFour, InvalidMoveError


def jugar(partida, columnas):
    """Juega varias columnas seguidas; los jugadores se alternan solos."""
    for columna in columnas:
        partida.drop(columna)


def test_la_ficha_cae_abajo_y_cambia_el_turno():
    # Arrange
    partida = ConnectFour()
    # Act
    fila = partida.drop(3)
    # Assert
    assert fila == ROWS - 1
    assert partida.grid[ROWS - 1][3] == 1
    assert partida.current_player == 2


def test_cuatro_en_vertical_gana():
    # Arrange
    partida = ConnectFour()
    # Act: X juega siempre la columna 1 y O la columna 2
    jugar(partida, [0, 1, 0, 1, 0, 1, 0])
    # Assert
    assert partida.winner == 1
    assert partida.is_over


def test_cuatro_en_diagonal_gana():
    # Arrange
    partida = ConnectFour()
    # Act: X arma una escalera de la columna 1 a la 4
    jugar(partida, [0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3])
    # Assert
    assert partida.winner == 1


def test_jugar_en_una_columna_llena_lanza_error():
    # Arrange: se llena la columna 1
    partida = ConnectFour()
    jugar(partida, [0] * ROWS)
    # Act + Assert
    with pytest.raises(InvalidMoveError, match="llena"):
        partida.drop(0)


@pytest.mark.parametrize("columna", [-1, COLS, "3", None])
def test_columnas_inexistentes_lanzan_error(columna):
    # Arrange
    partida = ConnectFour()
    # Act + Assert: negativa, fuera del tablero, texto y vacía
    with pytest.raises(InvalidMoveError):
        partida.drop(columna)


def test_detecta_la_columna_que_gana_la_partida():
    # Arrange: X tiene tres fichas en la base (columnas 1, 2 y 3)
    partida = ConnectFour()
    jugar(partida, [0, 6, 1, 6, 2])
    # Act
    ganadoras_de_x = partida.winning_moves(1)
    ganadoras_de_o = partida.winning_moves(2)
    # Assert: la columna 4 gana para X; O no tiene ninguna
    assert ganadoras_de_x == [3]
    assert ganadoras_de_o == []
