"""Player interactions."""

import dataclasses
from typing import Optional, Sequence, Tuple
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
    success: bool
    consumed: bool
    reason: str


@dataclasses.dataclass
class Use:
    name: str
    effects: Sequence[str]
    reason: str


def collide(speed, name):
    if walls.match(name) or walls.partial_match(name):
        return Collision(speed, "That's a wall...")
    elif name == 'house':
        return Collision(speed, "You don't want to go back in the house.")
    elif name == 'gate':
        return Collision(speed, "There's a gate here, but it's locked.")
    elif name == 'key':
        return Collision(speed, "It's some sort of key.")
    elif name.startswith('open_gate_'):
        return Collision(speed, 'You walk into the gate. Ouch.')
    elif name == 'hole':
        return Collision(speed, "It's a hole in the ground.")
    else:
        raise NotImplementedError(f'Collided with {name}')


def obtain(name):
    if walls.match(name) or walls.partial_match(name) or name in (
            'house', 'gate'):
        return None
    elif name == 'key':
        return Item(name, True, True, 'You pick up the key.')
    elif name == 'hole':
        return Item(name, False, False, 'You fall into the hole and climb back '
                    'out. You feel foolish.')
    else:
        raise NotImplementedError(f'Obtained {name}')


def use(name):
    if name == 'key':
        return Use('gate', ('open_gate_left', 'open_gate_right'),
                   'You unlock the gate.')
    else:
        raise NotImplementedError(f'Used {name}')
