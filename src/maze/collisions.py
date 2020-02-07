"""Player collisions."""

import dataclasses
from typing import Optional, Tuple
from . import walls


@dataclasses.dataclass
class Object:
    max_nocollision_speed: Optional[Tuple[int, int]]
    reason: str

    def closer_than(self, speed):
        # See play_area.Surface.check_player_collision. When two possible
        # collisions are in the same direction, the closer one is the one for
        # which the maximum speed that avoids collision is less.
        if self.max_nocollision_speed and speed:
            return abs(sum(self.max_nocollision_speed)) < abs(sum(speed))
        elif speed:
            return True
        else:
            return False


@dataclasses.dataclass
class Item(Object):
    name: str


def one(speed, name):
    if walls.match(name):
        return Object(speed, "That's a wall...")
    elif name == 'house':
        return Object(speed, "You don't want to go back in the house.")
    elif name == 'gate':
        return Object(speed, "There's a gate here, but it's locked.")
    else:
        return Item(speed, f'You pick up a {name}.', name)
