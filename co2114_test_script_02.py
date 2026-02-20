import unittest
import importlib.util
import sys
from pathlib import Path
from copy import deepcopy
from typing import override

from co2114.optimisation.adversarial import (
    Agent, AdversarialAgent, 
    Tile, Board, is_terminal, State, Numeric,
    TicTacToeGame, TicTacToeAgent)

global FILEPATH_AGENT

def load_class_from_file(filepath:Path, class_name:str) -> type:
    """ Utility function to load a class from a given file path 
    
    :param filepath: Path to the file containing the class.
    :param class_name: Name of the class to load.
    """
    spec = importlib.util.spec_from_file_location(filepath.stem, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    cls = getattr(module, class_name)
    return cls

def get_agent(instantiate=True) -> Agent | type[Agent]:
    """ Utility function to get a new agent instance
    
    :param instantiate: Whether to instantiate the class or return the class itself.
    :return: Instance of the agent class or the class itself.
    """
    cls = load_class_from_file(FILEPATH_AGENT, "AssignmentAgent02")

    return cls() if instantiate else cls


class MethodicalAgent(AdversarialAgent):
    """ Player agent that methodically picks the first available move from a list of possible moves. """
    def __init__(self, moveset:list[list[tuple[int, int]]], *args) -> None:
        """ Takes a predefined moveset to play through. 
        
        :param moveset: List of lists of (i,j) tuples representing moves to try in order.
        """
        super().__init__(*args)
        self.moveset = moveset
        self.move_index:int = 0
    
    def utility(self, action: tuple[str, State]) -> Numeric:
        """  Utility of a given action for the agent.
        
        Everything is equally good.
        
        :param action: Action tuple of ("move", State).
        :return: utility of action
        """
        return 1
    
    @override
    def program(self, percepts:State) -> tuple[str, State]:
        """ The agent's program.
        
        :param percepts: Current state of the game
        :return action: The action to be performed by the agent. Should be a tuple of ("move", state).
        """
        state = percepts
        valid_action = False
        while not valid_action:
            moves = self.moveset[self.move_index]
            print(moves)
            for i,j in moves:
                if not state[i][j].player: 
                    move = deepcopy(state)
                    move[i][j] = Tile(self.player)
                    assert self.utility(move) == 1
                    valid_action = True
                    self.move_index += 1
                    return ("move", move)
                else:
                    self.move_index += 1
                    continue
        raise IndexError(f"{self.__class__.__name__} ran out of moves!")


class DumbAgent(MethodicalAgent):
    """ A simple dumb agent for testing purposes. """
    def __init__(self, *args) -> None:
        moveset = [
            [(0,0)], [(0,1)], [(0,2)],
            [(1,0)], [(1,1)], [(1,2)],
            [(2,0)], [(2,1)], [(2,2)]]
        super().__init__(moveset, *args)


class SlightlyLessDumbAgent(MethodicalAgent):
    """ A slightly less dumb agent for testing purposes. """
    def __init__(self, *args) -> None:
        moveset = [
            [(1,1)],
            [(0,0), (0,2), (2,0), (2,2)],
            [(0,2), (2,0), (2,2)],
            [(2,0), (2,2)],
            [(2,2)],
            [(0,1), (1,0), (1,2), (2,1)],
            [(1,0), (1,2), (2,1)],
            [(1,2), (2,1)],
            [(2,1)]]
        super().__init__(moveset, *args)

    
class AgentvsAgentGame(TicTacToeGame):
    """ A simple TicTacToe game for two agents to play against each other. """
    def __init__(self, test_agent:Agent, *args, **kwargs) -> None:
        """ Embeds a test agent as the opponent
        
        :param test_agent: The agent to play against the main agent.
        """
        super().__init__(*args, **kwargs)
        self.test_agent = test_agent
    
    @override
    def add_agent(self, agent:Agent, player:str="X") -> None:
        """ Adds the player agent and sets up the test agent as the opponent.
        
        :param agent: The main agent to add to the game.
        :param player: The player identifier for the main agent ("X" or "O").
        """
        super().add_agent(agent, player)
        self.test_agent.player = "O" if player == "X" else "X"
    
    @override
    def make_move(self) -> None:
        """ Test Agent makes a move on the board. """
        agent = self.test_agent
    
        _, state = agent.program(deepcopy(self.board))
        self.execute_action(agent, ("move", state))
    
    @override
    def execute_action(self, agent: Agent, action: tuple[str, Board]) -> None:
        """ Indicates the agent's action before executing it.
        
        :param agent: The agent performing the action.
        :param action: The action to be performed.
        """
        print(f"{agent}: executing action: {action}")
        return super().execute_action(agent, action)
    

class TestAssignmentAgent02(unittest.TestCase):
    """ Seen problems for Assignment 01"""
    def test_instantiation(self):
        """ Runtime test 01: Does it instantiate? """
        agent_class = get_agent(instantiate=False)

        self.assertIsInstance(agent_class(), agent_class)

    def test_is_agent(self):
        """ Runtime test 02: Does it inherit from Agent? """
        agent = get_agent(instantiate=True)
        self.assertIsInstance(agent, Agent)

    def test_initialisation(self):
        """ Runtime test 03: Does it initialise correctly? """
        NotImplemented
        
    def test_default_case(self):
        """ Seen problem 01:
        
        Run the agent on the default test case.
        
        Plays the agent against a dumb opponent who does not make rational moves.
        """
        agent_class = get_agent(instantiate=False)
        player = "X"
        class TestAgent(DumbAgent, TicTacToeAgent):
            pass
        class PlayerAgent(agent_class, TicTacToeAgent):
            pass
        environment = AgentvsAgentGame(test_agent=TestAgent())
        environment.add_agent(PlayerAgent(), player=player)
        environment.run(pause_for_user=False)
        assert is_terminal(environment.board, return_winner=True) == player
        
    def test_case_slightly_less_dumb(self):
        """ Seen problem 02:
        
        Run the agent on a slightly more strategic (but still dumb) opponent.
        
        Plays the agent against a slightly less dumb opponent who still does not rational moves but has a better movelist.
        """
        agent_class = get_agent(instantiate=False)
        player = "X"
        class TestAgent(DumbAgent, TicTacToeAgent):
            pass
        class PlayerAgent(agent_class, TicTacToeAgent):
            pass
        environment = AgentvsAgentGame(test_agent=TestAgent())
        environment.add_agent(PlayerAgent(), player=player)
        environment.run(pause_for_user=False)
        assert is_terminal(environment.board, return_winner=True) == player
    
    def test_implementation(self):
        """ Seen problem 03
        
        Test implementation aspects
        
        Checks the appropriate number of moves have been made after a few steps.
        """
        agent_class = get_agent(instantiate=False)
        player = "X"
        
        class TestAgent(DumbAgent, TicTacToeAgent):
            pass
        
        class PlayerAgent(agent_class, TicTacToeAgent):
            pass
        
        environment = AgentvsAgentGame(test_agent=TestAgent())
        environment.add_agent(PlayerAgent(), player=player)
        
        def count_moves(board:Board) -> dict[str, int]:
            moves = {"X":0, "O":0}
            for row in board:
                for tile in row:
                    if tile.player is not None:
                        moves[tile.player] += 1
            return moves
        
        for i in range(3):
            with self.subTest(i=i):
                environment.step()
                moves = count_moves(environment.board)
                assert moves["X"] == i+1
                assert moves["O"] == i+1
            
    def test_utility(self):
        """ Seen problem 04
        
        Test implementation aspects
        
        Check that the utility values for terminal states are as expected.
        """
        agent_class = get_agent(instantiate=False)
        player = "X"
        
        class TestAgent(DumbAgent, TicTacToeAgent):
            pass
        
        class PlayerAgent(agent_class, TicTacToeAgent):
            pass
        
        environment = AgentvsAgentGame(test_agent=TestAgent())
        environment.add_agent(PlayerAgent(), player=player)
        
        boards = [[[Tile("X"), Tile("O"), Tile()],
                   [Tile("X"), Tile("O"), Tile()], 
                   [Tile("X"), Tile(), Tile("O")]],
                  [[Tile("X"), Tile("X"), Tile("O")],
                   [Tile("X"), Tile("O"), Tile()],
                   [Tile("O"), Tile(), Tile()]],
                  [[Tile("X"), Tile("O"), Tile("X")],
                   [Tile("X"), Tile("O"), Tile("O")],
                   [Tile("O"), Tile("X"), Tile("X")]]]
        
        win = environment.agent.utility(("move", boards[0]))
        loss = environment.agent.utility(("move", boards[1]))
        with self.subTest(i=0):
            assert win > loss
        with self.subTest(i=1):
            assert (win + loss) == 0  # zero sum
        with self.subTest(i=2):
            draw = environment.agent.utility(("move", boards[2]))
            assert draw == 0
            
    
    @classmethod
    def generate_summary(cls, result: unittest.TestResult) -> str:
        """Print counts and names of passed, failed, errors, skipped for this test case."""
        failed = [t.id() for t, _ in getattr(result, "failures", [])]
        errors = [t.id() for t, _ in getattr(result, "errors", [])]
        skipped = [t.id() for t, _ in getattr(result, "skipped", [])]
        all_tests = getattr(result, "all_tests", [])
        passed = [name for name in all_tests if name not in failed + errors + skipped]

        summary_str = ""
        summary_str += f"\nTest summary for {cls.__name__}:\n"
        summary_str += f"  Passed ({len(passed)}):\n"
        for n in passed:
            summary_str += f"    {n}\n"
        summary_str += f"  Failed ({len(failed)}):\n"
        for n in failed:
            summary_str += f"    {n}\n"
        summary_str += f"  Errors ({len(errors)}):\n"
        for n in errors:
            summary_str += f"    {n}\n"
        summary_str += f"  Skipped ({len(skipped)}):\n"
        for n in skipped:
            summary_str += f"    {n}\n"
        return summary_str


class ReportableResult(unittest.TextTestResult):
    """ Utility class to print out passed tests in addition to failed/error/skip. """
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.all_tests = []

    def startTest(self, test):
        # record test id on start so we can compute passed tests later
        self.all_tests.append(test.id())
        super().startTest(test)

if __name__ == "__main__":
    
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("agent_filepath", type=str,
        help="File path to the agent implementation to be tested.")
    args = parser.parse_args()

    FILEPATH_AGENT = Path(args.agent_filepath).resolve()

    if not FILEPATH_AGENT.is_file():
        # make sure file exists
        raise FileNotFoundError(
            f"Agent file not found at {FILEPATH_AGENT}")
    elif load_class_from_file(
            FILEPATH_AGENT, "AssignmentAgent02") is None:
        # make sure class exists
        raise ImportError(
            f"Could not find class AssignmentAgent02 in file {FILEPATH_AGENT}")

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAssignmentAgent02)

    runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=ReportableResult)
    
    result = runner.run(suite)
    summary = TestAssignmentAgent02.generate_summary(result)

    print(summary)