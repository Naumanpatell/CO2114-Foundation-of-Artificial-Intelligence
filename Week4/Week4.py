"""CO2114_LAB07.PY

Use this file to edit your Python code and 
try the exercises in Lab 03
"""

import math
import random
from typing import override

from co2114.optimisation.planning import *
from co2114.optimisation.things import *


#########################################################
#   Custom Environment (Correct Structure)
#########################################################

class HospitalPlacementEnv(HospitalPlacement):

    @override
    def percept(self, agent: Agent) -> tuple[State, list[State]]:
        return self.state, self.neighbours

    @property
    def state(self) -> State:
        return {
            "hospitals": {
                thing: thing.location
                for thing in self.things
                if isinstance(thing, Hospital)
            },
            "houses": {
                thing: thing.location
                for thing in self.things
                if isinstance(thing, House)
            },
            "bounds": {
                "xmin": 0,
                "xmax": self.width - 1,
                "ymin": 0,
                "ymax": self.height - 1,
            },
        }

    @property
    def neighbours(self) -> list[State]:
        neighbours = []

        for hospital, location in self.state["hospitals"].items():

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:

                new_location = (location[0] + dx, location[1] + dy)

                if self.is_inbounds(new_location):

                    candidate = self.state.copy()
                    candidate["hospitals"] = candidate["hospitals"].copy()
                    candidate["hospitals"][hospital] = new_location

                    neighbours.append(candidate)

        return neighbours

    @override
    def execute_action(self, agent: HospitalOptimiser, action: tuple[str, State]) -> None:
        command, state = action

        match command:
            case "done":
                agent.explore(state)
                self.success = True
            case "explore":
                agent.explore(state)

    @property
    def is_done(self) -> bool:
        if len(self.agents) == 0:
            return True
        return hasattr(self, "success") and self.success
    
    def explore(self, state:State) -> None:
        for hospital, loc in state["hospitals"].items():
            hospital.location = loc
    
    @override
    def utility(self, state: State) -> Numeric:
        obj = 0
        houses: dict[House, Location] = state["houses"]
        hospitals: dict[Hospital, Location] = state["hospitals"]

        for house in houses:
            dist_to_nearest = infinity
            for hospital in hospitals:
                house_loc = houses[house]
                hospital_loc = hospitals[hospital]

                dist = manhattan(house_loc, hospital_loc)

                if dist < dist_to_nearest:
                    dist_to_nearest = dist

            obj += dist_to_nearest

        return -obj

    
class HillClimbOptimiser(HospitalOptimiser):
    @override
    def program(self, 
                percepts:tuple[State, list[State]]) -> tuple[str, State | None]:
     
        state, neighbours = percepts
        objective = self.utility(state)
 
        print(f"{self}: current distance {-objective}")
        print(f"{self}: possible new objectives {[-self.utility(n) for n in neighbours]}")
        
        choice = self.maximise_utility(neighbours)
 
        if self.utility(choice) > objective:
            return ("explore", choice)
        else:
            return ("done", None)
        
class SimulatedAnnealingOptimiser(HospitalOptimiser):

    def __init__(self, num_steps: int = 100):
        super().__init__()
        self.t = 0
        self.tmax = num_steps

    def temperature(self) -> float:
        return max(0.01, self.tmax - self.t)

    def probability(self, delta: float, T: float) -> float:
        return math.exp(delta / T)

    @override
    def program(self, percepts: tuple[State, list[State]]) -> tuple[str, State | None]:

        state, neighbours = percepts

        if not neighbours:
            return ("done", None)

        T = self.temperature()
        self.t += 1

        if T <= 0:
            return ("done", None)

        choice = random.choice(neighbours)

        current_utility = self.utility(state)
        new_utility = self.utility(choice)

        delta = new_utility - current_utility

        if delta > 0:
            return ("explore", choice)
        else:
            P = self.probability(delta, T)
            if random.random() < P:
                return ("explore", choice)
            else:
                return ("explore", state)







#########################################################
#   Main Function
#########################################################

def main(graphical=True, steps=100, **kwargs):
    
    environment = generate_hospital_placement_env(**kwargs)

    agent = HillClimbOptimiser()
    environment.add_agent(agent)

    if graphical:
        environment.run(steps=steps, graphical=graphical, lps=8)
    else:
        environment.run(steps=steps, graphical=graphical)



#########################################################
#   Utility Code
#########################################################

def generate_hospital_placement_env(
        preset="0", hospitals=None, houses=None, height=None, width=None):

    if (hospitals and houses) or preset == "empty":

        environment = HospitalPlacementEnv(
            PRESET_STATES["empty"],
            height=10 if not height else height,
            width=20 if not width else width,
        )

        for _ in range(8 if not houses else houses):
            environment.add_thing_randomly(House())

        for _ in range(3 if not hospitals else hospitals):
            environment.add_thing_randomly(Hospital())

    else:

        environment = HospitalPlacementEnv(PRESET_STATES[preset])

        if preset == "2":
            for _ in range(2 if not hospitals else hospitals):
                environment.add_thing_randomly(Hospital())

    return environment


#########################################################
#   DO NOT EDIT BELOW
#########################################################

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="co2114_lab03")
    parser.add_argument("--test", action="store_true")
    parser.add_argument("-g", "--disable_gui", action="store_true")
    parser.add_argument("--houses", type=int)
    parser.add_argument("--hospitals", type=int)
    parser.add_argument("-y", "--height", type=int)
    parser.add_argument("-x", "--width", type=int)
    parser.add_argument("--preset", choices=list(PRESET_STATES.keys()))
    parser.add_argument("-t", "--steps", type=int, default=100)

    args = parser.parse_args()

    if args.test:
        from co2114.engine import ClockApp
        print("Running Demo Code")
        ClockApp.run_default()

    else:
        if args.hospitals and args.houses:
            main(
                not args.disable_gui,
                steps=args.steps,
                hospitals=args.hospitals,
                houses=args.houses,
                height=args.height,
                width=args.width,
            )
        elif args.preset:
            main(
                not args.disable_gui,
                steps=args.steps,
                preset=args.preset,
                hospitals=args.hospitals,
            )
        else:
            main(not args.disable_gui, args.steps)
