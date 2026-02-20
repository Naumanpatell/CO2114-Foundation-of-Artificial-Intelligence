from typing import override
from co2114.optimisation.adversarial import (
    State,
    Numeric,
    AdversarialAgent
)


class AssignmentAgent02(AdversarialAgent):

    def __init__(self):
        super().__init__()
        self.cache = {}

    def _state_key(self, state: State):
        return tuple(tuple(tile.player for tile in row) for row in state)

    def minimax(self, state, alpha, beta):
        key = self._state_key(state)

        if key in self.cache:
            return self.cache[key]

        score = self.score(state)
        if score is not None:
            self.cache[key] = score
            return score

        player_to_move = self.to_move(state)

        if player_to_move == "player":  
            value = float("-inf")
            for s in self.moves(state):
                value = max(value, self.minimax(s, alpha, beta))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
        else: 
            value = float("inf")
            for s in self.moves(state):
                value = min(value, self.minimax(s, alpha, beta))
                beta = min(beta, value)
                if beta <= alpha:
                    break

        self.cache[key] = value
        return value

    def utility(self, action: tuple[str, State]) -> Numeric:
        _, state = action
        return self.minimax(state, float("-inf"), float("inf"))

    @override
    def program(self, percepts: State) -> tuple[str, State]:
        best_value = float("-inf")
        best_state = None

        for s in self.moves(percepts):
            value = self.minimax(s, float("-inf"), float("inf"))
            if value > best_value:
                best_value = value
                best_state = s

        return ("move", best_state)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--play", action="store_true")
    args = parser.parse_args()

    if args.play:
        from co2114.optimisation.adversarial import (
            TicTacToeAgent,
            InteractiveTicTacToeGame
        )

        environment = InteractiveTicTacToeGame()

        class AgentPlayer(AssignmentAgent02, TicTacToeAgent):
            pass

        agent = AgentPlayer()
        environment.add_agent(agent, player="O")
        environment.run()
    else:
        agent = AssignmentAgent02()
        print("Sanity check passed.")