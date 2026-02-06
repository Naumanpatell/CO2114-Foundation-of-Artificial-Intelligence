from typing import override
import math

from co2114.search.graph import (
        ShortestPathAgent, 
        Node,
        Numeric
    )

class AssignmentAgent01(ShortestPathAgent):
    
    def __init__(self):
        super().__init__()
        self.frontier = []

    def heuristic(self, node: Node) -> Numeric:
        if self.target is None or node.location is None or self.target.location is None:
            return 0
        
        x1, y1 = node.location
        x2, y2 = self.target.location
        
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def f_score(self, node: Node) -> Numeric:
        if node not in self.dist:
            return float('inf')
        
        g_score = self.dist[node]
        h_score = self.heuristic(node)
        
        return g_score + h_score
    
    @override
    def explore(self, node:Node) -> None:
        self.location = node
        self.visited.add(node)
        if node in self.frontier:
            self.frontier.remove(node)


    @override
    def deliver(self, node:Node) -> tuple[list[Node], Numeric]:
        path = []
        current = node
        
        while current is not None:
            path.append(current)
            current = self.prev[current]
        
        path.reverse()
        distance = self.dist[node]
        
        return (path, distance)
            

    @override
    def program(self, percepts:list[tuple[Node, Numeric]]) -> tuple[str, Node]:
        for neighbor, edge_weight in percepts:
            new_distance = self.dist[self.location] + edge_weight
            
            if neighbor not in self.dist or new_distance < self.dist[neighbor]:
                self.dist[neighbor] = new_distance
                self.prev[neighbor] = self.location
                
                if neighbor not in self.visited and neighbor not in self.frontier:
                    self.frontier.append(neighbor)
        
        if self.at_goal:
            return ("deliver", self.target)
        
        next_node = None
        min_f_score = float('inf')
        
        for node in self.frontier:
            f = self.f_score(node)
            if f < min_f_score:
                min_f_score = f
                next_node = node
        
        return ("explore", next_node)


    @override
    def utility(self, action:tuple[str, Node]) -> Numeric:
        command, node = action
        
        if command == "explore":
            if node in self.dist:
                return -self.f_score(node)
            else:
                return float('-inf')
        
        return 0


if __name__ == "__main__":   
    def sanity_check():
        """ Simple sanity check for the AssignmentAgent01 class. """
        agent = AssignmentAgent01()
        print("Sanity check passed.")

    sanity_check()