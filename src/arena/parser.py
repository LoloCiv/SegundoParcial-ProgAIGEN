"""Convierte la respuesta de texto del modelo en una columna del motor (0-6)."""

import json
import re

from .engine import COLS


class MoveParseError(ValueError):
    """La respuesta del modelo no contiene una jugada utilizable."""


def parse_move(text: str) -> tuple[int, str]:
    """Interpreta el JSON de jugada y adapta la columna al índice del motor.

    Tolera texto antes o después del primer objeto JSON encontrado y acepta
    que el valor de ``columna`` sea convertible a entero.

    Args:
        text: Respuesta del modelo con ``columna`` entre 1 y 7 y, opcionalmente,
            ``razon``.

    Returns:
        Tupla con la columna convertida al rango 0–6 y la razón como texto.

    Raises:
        MoveParseError: Si la respuesta no es texto, no contiene un JSON
            válido, no incluye ``columna`` o el valor no queda entre 1 y 7.
    """
    if not isinstance(text, str):
        raise MoveParseError("la respuesta no es texto")

    json_match = re.search(r"\{.*?\}", text, re.DOTALL)
    if json_match is None:
        raise MoveParseError("la respuesta no contiene un JSON")

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as error:
        raise MoveParseError(f"JSON inválido: {error}") from error

    if not isinstance(data, dict) or "columna" not in data:
        raise MoveParseError("el JSON no tiene el campo 'columna'")

    try:
        column_1_to_7 = int(data["columna"])
    except (TypeError, ValueError) as error:
        raise MoveParseError(f"columna no numérica: {data['columna']!r}") from error

    if not 1 <= column_1_to_7 <= COLS:
        raise MoveParseError(f"columna {column_1_to_7} fuera del rango 1-{COLS}")

    return column_1_to_7 - 1, str(data.get("razon", ""))
