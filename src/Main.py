from Lambda import Wrapper
from Games.Mezzonic import MezzonicGame
from Games import *
from Errors import *
from ResultsCache import RESULTS_CACHE

from typing import Dict, Type

SUPPORTED_GAMES: Dict[str, Type[Game]] = {
    g.name(): g for g in [MezzonicGame]
}


def main(event, context):
    with Wrapper(event, context, verbose=True) as w:

        w.add_cors_header()

        game_name: str = w.args.get_query("game", val_type=str)
        if not game_name or game_name not in SUPPORTED_GAMES:
            raise ExecutionError(ErrorType.BAD_REQUEST,
                                 f"Unsupported game '{game_name}'.", {})

        game = SUPPORTED_GAMES[game_name].prepare(w.args)

        conditions = game.conditions()

        if conditions in RESULTS_CACHE:
            print(f"RESULT FOUND IN CACHE!")

        else:
            RESULTS_CACHE[conditions] = game.solve()

        result = RESULTS_CACHE[conditions]

        #

        print(f"Found solution: "
              f"{' -> '.join(str(transition.value) for state, transition in result if transition is not None)}")

        w.set_result(result)

    return w.result


if __name__ == '__main__':
    main({
        "queryStringParameters": {
            # "board": "11000|00100|11101|01111|00010",
            # 1,1 => 1,0 => 3,2 => 4,3 => 3,4

            # "board": "01000|00100|01100|11111|00010",

            # "board": "01101|00000|10110|10001|00000",

            # "board": "00010|00000|01000|00000|00000",

            # "board": "00000|00000|00100|00000|00000",

            "board": "11100|01001|10011|01011|01111",

            "algorithm": "exhaustive",
            "game": "mezzonic"
        },
        "body": {
            "lookahead_steps": 1,
            "mode": "sorted_breadth_first",
            "limit": 5
        }
    }, {})
