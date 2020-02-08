"""Player interactions."""

import dataclasses
from typing import Optional, Tuple
from . import walls


@dataclasses.dataclass
class Collision:
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
class Item:
    name: str
    reason: str


def collide(speed, name):
    if walls.match(name):
        return Collision(speed, "That's a wall...")
    elif name == 'house':
        return Collision(speed, "You don't want to go back in the house.")
    elif name == 'gate':
        return Collision(speed, "There's a gate here, but it's locked.")
    elif name == 'key':
        return Collision(speed, "It's some sort of key.")
    else:
        raise NotImplementedError(f'Collided with {name}')


def pick_up(name):
    if name == 'key':
        return Item(name, 'You pick up the key.')
    else:
        raise NotImplementedError(f'Picked up {name}')
