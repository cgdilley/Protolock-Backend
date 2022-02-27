from __future__ import annotations

from Lambda import LambdaArguments
from Games.Game import Game
from Games.Mezzonic.Board import Board, BoardTransition
from PathFinding import Algorithm, BasicAlgorithm, LookaheadAlgorithm, OrderlessAlgorithm, OrderlessLookaheadAlgorithm
from Games.Mezzonic.ExhaustiveMezzonicAlgorithm import ExhaustiveMezzonicAlgorithm
from Errors import *

from typing import List, Type
import json

SIZE_LIMIT = (10, 10)


class MezzonicGame(Game[Board, BoardTransition]):

    def __init__(self, initial_state: Board, algorithm: Algorithm):
        super(MezzonicGame, self).__init__(initial_state, algorithm)

    @classmethod
    def name(cls) -> str:
        return "mezzonic"

    @classmethod
    def prepare(cls, args: LambdaArguments) -> MezzonicGame:
        board_str: str = args.get_query("board", val_type=str, default=None)
        if not board_str:
            raise ExecutionError(ErrorType.BAD_REQUEST, "Invalid board.",
                                 {"given": {"board": board_str if board_str else None}})
        board: Board = Board.parse(board_str)
        algo_name: str = args.get_query("algorithm", val_type=str, default=cls.supported_algorithms()[0].name())
        algo_args: dict = args.body

        if board.height > SIZE_LIMIT[0] or board.width > SIZE_LIMIT[1]:
            raise ExecutionError(ErrorType.BAD_REQUEST, "Given board is too large.",
                                 {"given": {"size": f"({board.height}x{board.width})",
                                            "limit": f"({SIZE_LIMIT[0]}x{SIZE_LIMIT[1]})"}})

        return MezzonicGame(board, cls._load_algorithm(algo_name, algo_args))

    def log(self) -> None:
        print(f"BOARD ({self.initial_state.width}x{self.initial_state.height}):\n{self.initial_state.render()}")
        print(f"ALGORITHM: {self.algorithm.name()} ({self.algorithm.__class__.__name__}")
        print(f"ARGS: {json.dumps(self.algorithm.kwargs)}")

    @classmethod
    def supported_algorithms(cls) -> List[Type[Algorithm]]:
        return [ExhaustiveMezzonicAlgorithm, OrderlessAlgorithm, OrderlessLookaheadAlgorithm,
                BasicAlgorithm, LookaheadAlgorithm]
