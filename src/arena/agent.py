"""El agente LLM: arma el prompt con sus skills, consulta al modelo y valida la jugada.

Flujo de cada turno (``LLMAgent.choose_move``):
  1. Prompt de sistema = rol del .agent.md + una sección por cada skill.
  2. Prompt del turno = tablero, columnas legales y amenazas (calculadas por código).
  3. El modelo responde JSON; si la jugada es inválida se reintenta con el error.
  4. Si tras los reintentos sigue mal, se juega una columna legal al azar (fallback).
"""

import random
from dataclasses import dataclass

from .engine import SYMBOLS, ConnectFour, opponent_of
from .ollama_client import OllamaClient
from .parser import MoveParseError, parse_move
from .skills import AgentConfig, Skill

MAX_RETRIES = 2  # reintentos después del primer intento


@dataclass(frozen=True)
class MoveDecision:
    """Jugada elegida y métricas del proceso que la produjo.

    Attributes:
        column: Índice de columna del motor, entre 0 y 6.
        reason: Explicación de la jugada, si la respuesta la incluye.
        invalid_attempts: Respuestas inválidas recibidas antes de elegir.
        fallback: Indica si la columna se eligió al azar tras agotar intentos.
        latency_s: Latencia acumulada de las consultas.
        prompt_tokens: Tokens de entrada acumulados.
        completion_tokens: Tokens generados acumulados.
    """

    column: int  # 0-6
    reason: str = ""
    invalid_attempts: int = 0  # respuestas inválidas antes de acertar
    fallback: bool = False  # True si hubo que jugar al azar
    latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0


def build_system_prompt(config: AgentConfig, skills: list[Skill]) -> str:
    """Combina las instrucciones del agente con las skills seleccionadas.

    Args:
        config: Configuración declarativa del agente.
        skills: Skills que se agregan en el orden recibido.

    Returns:
        Prompt de sistema con el cuerpo del agente y las secciones de skills.
    """
    sections = [config.body]
    for skill in skills:
        sections.append(f"## Skill: {skill.name}\n{skill.body}")
    return "\n\n".join(sections)


def build_turn_prompt(game: ConnectFour, player: int) -> str:
    """Construye el mensaje de usuario que describe el estado de la partida.

    Args:
        game: Estado actual del tablero.
        player: Identificador del jugador al que se le pide mover.

    Returns:
        Texto con tablero, columnas legales, amenazas inmediatas e instrucciones
        para responder en JSON. Las columnas del mensaje van de 1 a 7.
    """
    legal_columns = [column + 1 for column in game.legal_moves()]
    winning_columns = [column + 1 for column in game.winning_moves(player)]
    blocking_columns = [column + 1 for column in game.winning_moves(opponent_of(player))]
    if game.moves:
        last_move = f"columna {game.moves[-1] + 1}"
    else:
        last_move = "ninguno (abrís la partida)"

    return (
        f"Vos jugás con {SYMBOLS[player]}. El rival juega con {SYMBOLS[opponent_of(player)]}.\n"
        f"Tablero (fila superior arriba, columnas 1-7):\n{game.render()}\n\n"
        f"Columnas legales: {legal_columns}\n"
        f"Columnas con las que ganás ahora mismo: {winning_columns or 'ninguna'}\n"
        f"Columnas que bloquean una victoria inmediata del rival: {blocking_columns or 'ninguna'}\n"
        f"Último movimiento del rival: {last_move}\n\n"
        'Respondé solo con JSON: {"columna": <1-7>, "razon": "<una frase>"}'
    )


class LLMAgent:
    """Jugador de Ollama configurado con un archivo de agente y skills."""

    def __init__(self, config: AgentConfig, skills: list[Skill], client: OllamaClient,
                 label: str | None = None, seed: int | None = None) -> None:
        """Inicializa el agente y su generador aleatorio para el fallback.

        Args:
            config: Modelo, opciones e instrucciones del agente.
            skills: Skills que se incluirán en el prompt.
            client: Cliente que consulta Ollama.
            label: Nombre visible opcional; por omisión se arma con agente y
                personalidad.
            seed: Semilla aleatoria opcional; si falta, se usa la opción
                ``seed`` de la configuración.
        """
        self.config = config
        self.skills = skills
        self.client = client
        self.random = random.Random(seed if seed is not None else config.options.get("seed"))

        personality = next((s.name for s in skills if s.kind == "personalidad"), "sin personalidad")
        self.name = label or f"{config.name} ({personality})"

    def choose_move(self, game: ConnectFour, player: int) -> MoveDecision:
        """Solicita una jugada, valida la columna y reintenta si es inválida.

        Args:
            game: Estado actual de la partida.
            player: Identificador del jugador que debe mover.

        Returns:
            Decisión con columna legal y métricas. Después de un intento
            inicial y hasta ``MAX_RETRIES`` reintentos fallidos, elige una
            columna legal al azar y marca ``fallback``.

        Raises:
            OllamaError: Si una consulta al cliente Ollama falla.
        """
        legal_columns = game.legal_moves()
        messages = [
            {"role": "system", "content": build_system_prompt(self.config, self.skills)},
            {"role": "user", "content": build_turn_prompt(game, player)},
        ]
        invalid_attempts = prompt_tokens = completion_tokens = 0
        latency_s = 0.0

        for _ in range(MAX_RETRIES + 1):
            reply = self.client.chat(self.config.model, messages, self.config.options)
            latency_s += reply.latency_s
            prompt_tokens += reply.prompt_tokens
            completion_tokens += reply.completion_tokens

            try:
                column, reason = parse_move(reply.content)
                if column not in legal_columns:
                    raise MoveParseError(f"la columna {column + 1} no es legal")
            except MoveParseError as error:
                # Le mostramos al modelo su error para que corrija en el siguiente intento
                invalid_attempts += 1
                messages.append({"role": "assistant", "content": reply.content})
                messages.append({"role": "user", "content": f"Jugada inválida: {error}. Elegí una columna legal y respondé solo con JSON."})
                continue

            return MoveDecision(column, reason, invalid_attempts, False, latency_s, prompt_tokens, completion_tokens)

        # El modelo no logró una jugada válida: se juega al azar para no frenar la partida
        random_column = self.random.choice(legal_columns)
        return MoveDecision(random_column, "jugada aleatoria: el modelo no dio una jugada válida",
                            invalid_attempts, True, latency_s, prompt_tokens, completion_tokens)
