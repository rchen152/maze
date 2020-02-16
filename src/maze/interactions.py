"""Player interactions."""

import dataclasses
import enum
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


class UseEffectType(enum.Enum):
    REMOVE_OBJECT = enum.auto()
    ADD_OBJECT = enum.auto()


@dataclasses.dataclass
class UseEffect:
    type: UseEffectType
    target: str

    @classmethod
    def remove(cls, obj):
        return cls(UseEffectType.REMOVE_OBJECT, obj)

    @classmethod
    def add(cls, obj):
        return cls(UseEffectType.ADD_OBJECT, obj)


@dataclasses.dataclass
class Use:
    activator: str
    effects: Sequence[UseEffect]
    reason: str


def _collision_reason(name):
    if walls.match(name) or walls.partial_match(name):
        return "That's a wall..."
    elif name == 'house':
        return "You don't want to go back in the house."
    elif name == 'key':
        return "It's some sort of key."
    elif name == 'gate':
        return "There's a gate here, but it's locked."
    elif name.startswith('open_gate_'):
        return 'You walk into the gate. Ouch.'
    elif name.startswith('block_'):
        return 'An oversized alphabet block. How curious.'
    elif name == 'eggplant':
        return 'An eggplant. Ew.'
    elif name == 'trash_can':
        return 'Do you still have the eggplant?'
    elif name == 'fishing_rod':
        return 'Who left a fishing rod here?'
    elif name == 'lake':
        return 'What a lovely calm lake.'
    elif name == 'angry_cat':
        return 'Your way is blocked by an angry cat.'
    elif name == 'hole':
        return "It's a hole in the ground."
    else:
        raise NotImplementedError(f'Collided with {name}')


def collide(speed, name):
    return Collision(speed, _collision_reason(name))


def obtain(name):
    if name == 'key':
        return Item(name, True, True, 'You pick up the key.')
    elif name.startswith('block_'):
        return Item(
            name, True, True,
            'You decide to carry the giant wooden block around with you.')
    elif name == 'eggplant':
        return Item(
            name, True, True, 'You gingerly pick up the disgusting vegetable.')
    elif name == 'fishing_rod':
        return Item(name, True, True, "You steal someone's fishing rod.")
    elif name == 'hole':
        return Item(name, False, False, 'You fall into the hole and climb back '
                    'out. You feel foolish.')
    else:
        return None


def use(name):
    if name == 'key':
        return [Use('gate', (UseEffect.remove('gate'),
                             UseEffect.add('open_gate_left'),
                             UseEffect.add('open_gate_right')),
                    'You unlock the gate.')]
    elif name.startswith('block_'):
        return []
    elif name == 'eggplant':
        return [Use('angry_cat', (),
                    'You feed the cat the eggplant. It is even angrier now.'),
                Use('trash_can', (), "Yeah, you don't need that.")]
    elif name == 'fishing_rod':
        return [Use('lake', (), "You can't catch fish yet.")]
    else:
        raise NotImplementedError(f'Used {name}')
