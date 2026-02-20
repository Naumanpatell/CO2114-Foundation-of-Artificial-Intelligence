import unittest
import importlib.util
import sys
from pathlib import Path

from co2114_.search.graph import Agent, ShortestPathEnvironment


# from template import AssignmentAgent01

TEST_CASE_01: dict[str, list[str | tuple[str,str] | int]]= {
    "vertices": ["A","B","C","D","E","F"],
    "edges":[
        ("A","B"),("A","D"),("B","D"),("B","C"),
        ("D","C"),("C","E"),("C","F"),("E","F")],
    "weights": [2, 8, 5, 6, 3, 1, 9, 3]
}  # simple graph for testing

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
    cls = load_class_from_file(FILEPATH_AGENT, "AssignmentAgent01")

    return cls() if instantiate else cls

class TestAssignmentAgent01(unittest.TestCase):
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
        environment = ShortestPathEnvironment.from_dict(TEST_CASE_01)
        agent = get_agent(instantiate=True)
        environment.add_agent(agent, init="A", target="F")
        self.assertEqual(agent.init.label, "A")
        self.assertEqual(agent.location.label, "A")
        self.assertEqual(agent.target.label, "F")

    def test_default_case(self):
        """ Seen problem 01:
        
        Run the agent on the default test case.
        
        Check that it reaches the goal, and that the shortest path and distances are correct.
        """
        graph = TEST_CASE_01
        environment = ShortestPathEnvironment.from_dict(graph)
        
        agent = get_agent(instantiate=True)
        environment.add_agent(agent, init="A", target="F")
        environment.run(pause_for_user=False)

        self.assertTrue(agent.at_goal)
        self.assertIn(agent.init, agent.dist)
        self.assertIn(agent.target, agent.dist)

        self.assertEqual(agent.dist[agent.init], 0)
        self.assertEqual(agent.dist[agent.target], 12)

        shortest_path = [node.label 
            for node in environment.shortest_path[agent.init][agent.target][0]]
        self.assertSequenceEqual(
            shortest_path,
            ['A', 'B', 'C', 'E', 'F'])
    
        
    def test_implementation(self):
        """ Seen problem 02
        
        Test implementation aspects
        
        During the first 4 steps, check that the utility values computed
        for the explored nodes are as expected.
        """
        graph = TEST_CASE_01
        environment = ShortestPathEnvironment.from_dict(graph)

        agent = get_agent(instantiate=True)
        environment.add_agent(agent, init="A", target="F")
        
        _test_util = (
            {-2, -8},
            {0, -7, -8},
            {0, -7, -8},
            {-2, -7, -9, -17}
        )

        for i in range(4):
            with self.subTest(i=i):
                environment.step() # 1 iteration
                utilities = {
                    agent.utility(("explore", node))
                    for node in agent.prev[agent.location].neighbours}
                self.assertSetEqual(
                    utilities,
                    _test_util[i]
                )

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
            FILEPATH_AGENT, "AssignmentAgent01") is None:
        # make sure class exists
        raise ImportError(
            f"Could not find class AssignmentAgent01 in file {FILEPATH_AGENT}")

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestAssignmentAgent01)

    runner = unittest.TextTestRunner(
        verbosity=2,
        resultclass=ReportableResult)
    
    result = runner.run(suite)
    summary = TestAssignmentAgent01.generate_summary(result)

    print(summary)