from ..search import things

from ..util.fonts import platform

from typing import override

# Re-export relevant classes from things module
Agent = things.Agent
UtilityBasedAgent = things.UtilityBasedAgent

class Hospital(things.Thing):
    @override
    def __repr__(self):
        """ String representation of a Hospital. """
        return "🏥" if platform != "darwin" else "+"

class House(things.Thing):
    @override
    def __repr__(self):
        """ String representation of a House. """
        return "🏠" if platform != "darwin" else "^"

class Optimiser(things.Agent):
    @override
    def __repr__(self):
        """ String representation of an Optimiser. """
        return "📈"