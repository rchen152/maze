"""Player interactions."""

import dataclasses
import enum
from typing import Optional, Sequence, Tuple, Union
from . import walls

Speed = Tuple[int, int]


@dataclasses.dataclass
class Collision:
    max_nocollision_speed: Optional[Speed]
    reason: str

    def closer_than(self, speed):
        # See play_area.Surface._check_player_collision. When two possible
        # collisions are in the same direction, the closer one is the one for
        # which the maximum speed that avoids collision is less.
        if self.max_nocollision_speed and speed:
            return abs(sum(self.max_nocollision_speed)) < abs(sum(speed))
        elif speed:
            return True
        else:
            return False


class ItemEffectType(enum.Enum):
    REMOVE = enum.auto()
    ADD = enum.auto()


class ObjectEffectType(enum.Enum):
    REMOVE = enum.auto()
    ADD = enum.auto()


@dataclasses.dataclass
class Effect:
    type: Union[ItemEffectType, ObjectEffectType]
    target: str

    @classmethod
    def remove_item(cls, item):
        return cls(ItemEffectType.REMOVE, item)

    @classmethod
    def add_item(cls, item):
        return cls(ItemEffectType.ADD, item)

    @classmethod
    def remove_object(cls, obj):
        return cls(ObjectEffectType.REMOVE, obj)

    @classmethod
    def add_object(cls, obj):
        return cls(ObjectEffectType.ADD, obj)


@dataclasses.dataclass
class Item:
    item_effects: Sequence[Effect]
    object_effects: Sequence[Effect]
    reason: str


@dataclasses.dataclass
class Use:
    activator: str
    item_effects: Sequence[Effect]
    object_effects: Sequence[Effect]
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


def collide(speed, name) -> Collision:
    return Collision(speed, _collision_reason(name))


def _simple_obtain_effects(name):
    return [(Effect.add_item(name),), (Effect.remove_object(name),)]


def obtain(name) -> Optional[Item]:
    if name == 'key':
        return Item(*_simple_obtain_effects(name), 'You pick up the key.')
    elif name.startswith('block_'):
        return Item(
            *_simple_obtain_effects(name),
            'You decide to carry the giant wooden block around with you.')
    elif name == 'eggplant':
        return Item(*_simple_obtain_effects(name),
                    'You gingerly pick up the disgusting vegetable.')
    elif name == 'fishing_rod':
        return Item(*_simple_obtain_effects(name),
                    "You steal someone's fishing rod.")
    elif name == 'hole':
        return Item(
            (), (),
            'You fall into the hole and climb back out. You feel foolish.')
    else:
        return None


def use(name) -> Sequence[Use]:
    if name == 'key':
        object_effects = (Effect.remove_object('gate'),
                          Effect.add_object('open_gate_left'),
                          Effect.add_object('open_gate_right'))
        return [Use('gate', (Effect.remove_item('key'),), object_effects,
                    'You unlock the gate.')]
    elif name.startswith('block_'):
        return []
    elif name == 'eggplant':
        return [Use('angry_cat', (Effect.remove_item('eggplant'),), (),
                    'You feed the cat the eggplant. It is even angrier now.'),
                Use('trash_can', (Effect.remove_item('eggplant'),), (),
                    "Yeah, you don't need that.")]
    elif name == 'fishing_rod':
        return [Use('lake', (), (), "You can't catch fish yet.")]
    else:
        raise NotImplementedError(f'Used {name}')
