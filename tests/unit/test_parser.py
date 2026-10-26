"""Pruebas unitarias del intérprete de respuestas del modelo (src/arena/parser.py)."""

import pytest

from arena.parser import MoveParseError, parse_move


def test_lee_un_json_limpio():
    # Arrange
    respuesta = '{"columna": 4, "razon": "centro"}'
    # Act
    columna, razon = parse_move(respuesta)
    # Assert: el modelo habla en 1-7, el motor en 0-6
    assert columna == 3
    assert razon == "centro"


def test_tolera_texto_alrededor_del_json():
    # Arrange
    respuesta = 'Claro, juego así: {"columna": 1, "razon": "borde"} ¡listo!'
    # Act
    columna, _ = parse_move(respuesta)
    # Assert
    assert columna == 0


@pytest.mark.parametrize("respuesta", ["", "hola", "{}", '{"columna": "abc"}', "{'columna': 5}"])
def test_respuestas_sin_jugada_lanzan_error(respuesta):
    # Act + Assert: vacía, sin JSON, sin columna, columna no numérica y JSON mal escrito
    with pytest.raises(MoveParseError):
        parse_move(respuesta)


@pytest.mark.parametrize("columna", [0, 8])
def test_columna_fuera_de_1_a_7_lanza_error(columna):
    # Arrange
    respuesta = '{"columna": %d}' % columna
    # Act + Assert
    with pytest.raises(MoveParseError, match="fuera del rango"):
        parse_move(respuesta)
