from numpy import inf as infinity
from ..optimisation.things import *
from ..agent.environment import GraphicEnvironment
from ..search.util import manhattan
import random

from typing import override

Location = tuple[int, int]
State = None | dict[str, dict[House | Hospital, Location] | dict[str, int]]
Numeric = int | float
PRESET_STATES: dict[str, dict[str, list[Location] | int]] = {
    "empty": None,
    '0': {
        "hospitals": [(2, 4)],
        "houses": [(2,1),(1,3),(8,0),(6,4)],
        "height": 5,
        "width": 10,
    },
    '1': {
        "hospitals": [(4,0), (9,3)],
        "houses": [(2,1),(1,3),(8,0),(6,4)],
        "height": 5, 
        "width": 10},
    '2': {
        "houses": [(2,1),(1,3),(8,0),(6,4)],
        "height": 5, 
        "width": 10},
    '3': {
        "houses": [(1, 2), (5, 1), (12, 2), (13, 2), (4, 0), (8, 5), (15, 1), (12, 4), (1, 7), (6, 5), (15, 3), (0, 1), (0, 0), (10, 5), (5, 3), (3, 6), (6, 3), (0, 7)],
        "hospitals": [(11,6), (5,2), (4,1)],
        "height": 8,
        "width": 16},
    '4': {
        "houses": [(1, 14), (17, 6), (2, 4), (4, 17), (9, 4), (3, 14), (8, 1), (17, 15), (6, 10), (9, 7), (3, 19), (10, 11), (8, 18), (0, 15), (4, 15), (4, 7), (16, 11), (5, 8), (13, 12), (8, 13), (17, 3), (1, 13), (11, 9), (10, 15), (2, 3), (7, 10), (5, 1), (14, 19), (14, 7), (18, 6), (8, 3), (11, 2), (5, 7), (11, 8), (18, 16), (12, 13), (5, 2), (18, 14)],
        "hospitals": [(8,0), (0, 12), (17, 12), (3,5)],
        "height": 20,
        "width": 20},
    '5': {
        "houses": [ (26, 22), (8, 13), (5, 29), (19, 15), (27, 13), (17, 24), (15, 6), (0, 11), (0, 26), (1, 22), (0, 14), (13, 17), (4, 10), (27, 10), (28, 28), (26, 29), (17, 28), (10, 18), (3, 8), (25, 6), (16, 28), (1, 15), (10, 23), (10, 6), (26, 15), (15, 12), (27, 12), (13, 1), (15, 10), (9, 29), (22, 9), (17, 29), (21, 24), (12, 17), (8, 15), (19, 13), (1, 26), (12, 18), (20, 3), (15, 18), (16, 27), (25, 18), (4, 17), (21, 13), (6, 29), (10, 25), (15, 23), (18, 12), (8, 20), (11, 18), (10, 19), (9, 26), (9, 23), (17, 1), (24, 10), (11, 4), (3, 3), (8, 12), (22, 10), (12, 21), (19, 28), (21, 29), (10, 17), (27, 1), (26, 9), (9, 14), (21, 15), (29, 18), (20, 15), (13, 12), (24, 17), (7, 20), (28, 4), (19, 17), (1, 8), (26, 26), (11, 28), (2, 1)],
        "hospitals": [(15, 5), (6, 1), (11, 3), (27, 22), (8, 14)],
        "height": 30,
        "width": 30},
}



class HospitalOptimiser(Optimiser, UtilityBasedAgent):
    """ Hospital Optimiser Agent"""
    def explore(self, state:State) -> None:
        """ Move hospitals to new locations in state
        
        :param state: new state with hospital locations
        """
        if not state: return
        print(f"{self}: exploring state\n    {state['hospitals']}")
        for hospital, loc in state["hospitals"].items():
            hospital.location = loc

    @override
    def utility(self, state:State) -> Numeric:
        """ Calculate utility of possible state by calculating distance
            of each hospital to houses
        
        Returns negative total distance to be minimised.

        :param state: current state with hospital and house locations
        :return: negative total distance
        """
        obj = 0
        houses: dict[House, Location] = state["houses"]  # type: ignore
        hospitals: dict[Hospital, Location] = state["hospitals"]  # type: ignore

        for house in houses: # iterate over houses
            dist_to_nearest_hospital = infinity   # very big

            for hospital in hospitals:  # iterate over hospitals
                house_loc    = houses[house]
                hospital_loc = hospitals[hospital]

                dist = manhattan(house_loc, hospital_loc)

                # calculate closest distance
                if dist < dist_to_nearest_hospital:
                    dist_to_nearest_hospital = dist

            obj += dist_to_nearest_hospital # add distance for this house
        return -obj


class HospitalPlacement(GraphicEnvironment):
    """ Hospital Placement Environment
     
    Allows placement of hospitals and houses on a grid
    
    Has a state consisting of hospital and house locations and bounds of the environment
    """
    def __init__(self,
                 init:dict[str, list[Location] | int] | None = None,
                 *args,
                 **kwargs) -> None:
        """ Constroctor for HospitalPlacement environment
        
        :param init: initial state dictionary with hospital and house locations and height/width of environment
        :param args: additional args for GraphicEnvironment
        :param kwargs: additional kwargs for GraphicEnvironment
        """
        super().__init__(*args, **kwargs)
        self.initialise_state(init)
 

    def initialise_state(self,
                         state_dict: dict[str, list[Location] | int]) -> None:
        """ Initialise environment state from state dictionary 
        
        :param state_dict: state dictionary with hospital and house locations and height/width of environment
        """
        if state_dict is None: return  # empty state

        if "height" in state_dict:
            self.height = state_dict["height"]

        if "width" in state_dict:
            self.width = state_dict["width"]

        self.size = self.width, self.height

        if "hospitals" in state_dict:
            for loc in state_dict["hospitals"]:
                self.add_thing(Hospital(), location=loc)

        for loc in state_dict["houses"]:
            self.add_thing(House(), location=loc)


    @property
    def state(self) -> State:
        """ Attribute returning current environment state 
        
        :return: current state with hospital and house locations and bounds of environment
        """
        return {
            "hospitals": {
                thing: thing.location
                    for thing in self.things
                        if isinstance(thing, Hospital)},
            "houses": {
                thing: thing.location
                    for thing in self.things
                        if isinstance(thing, House)},
            "bounds": {
                "xmin": 0, "xmax": self.width-1,
                "ymin": 0, "ymax": self.height-1}
        }

    @property
    def neighbours(self) -> list[State]:
        """ Generate neighbouring states by moving each hospital
            in each direction by one unit if possible.

        :return: list of neighbouring states
        """
        neighbours = []
        for i, hospital in enumerate(self.state["hospitals"]):
            location = hospital.location
            for x,y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                proposal = location[0] + x, location[1] + y
                if self.is_inbounds(proposal):
                    candidate = self.state.copy()
                    candidate["hospitals"][hospital] = proposal
                    neighbours.append(candidate)
        return neighbours

    def is_inbounds(self, location:Location) -> bool:
        """ Checks if location is in bounds and unoccupied
        
        :return bool: True if location is in bounds and unoccupied
        """
        if not super().is_inbounds(location):
            return False
        return len(self.things_at(location)) == 0

    @override
    def add_agent(self, agent:Agent) -> None:
        """ Add agent to environment, overrides GraphicEnvironment method as agent has no location.
        
        :param agent: agent to add
        """
        if not isinstance(agent, Agent):
            raise TypeError(f"{self}: {agent} is not an Agent.")
        self.agents.add(agent)

    @override
    def add_thing_randomly(self, thing:things.Thing) -> None:
        """ Add thing to random unoccupied location in environment
        
        :param thing: thing to add
        """
        x = random.randint(self.x_start, self.x_end-1)
        y = random.randint(self.y_start, self.y_end-1)
        lim, count = 10, 0
        while not self.is_inbounds((x,y)):
            count += 1
            if count > lim:
                print(f"Tried and failed to add {thing} to environment")
                return     
            x = random.randint(self.x_start, self.x_end-1)
            y = random.randint(self.y_start, self.y_end-1)
        self.add_thing(thing, (x,y))

    @property
    def is_done(self) -> bool:
        """ Definition of when environment is done """
        if len(self.agents) == 0: return True  # if there are no agents
        return hasattr(self, "success") and self.success

    @override
    def percept(self, agent:Agent) -> tuple[State, list[State]]:
        """ Percept for agent in environment
        
        :return tuple: current state and neighbouring states
        """
        return self.state, self.neighbours

    @override
    def execute_action(self,
                       agent:HospitalOptimiser,action:tuple[str,State]) -> None:
        """ Execute an action 
        
        :param agent: agent performing action
        :param action: action to execute, tuple of command and state. possible commands are "done" and "explore"
        """
        command, state = action
        match command:
            case "done":  # optimisation complete
                if state:
                    agent.explore(state)
                self.success = True
            case "explore":
                agent.explore(state)