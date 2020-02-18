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
    activator: Optional[str]
    item_effects: Sequence[Effect]
    object_effects: Sequence[Effect]
    reason: str


def _collision_reason(name):
    if walls.match(name) or walls.partial_match(name):
        return "That's a wall..."
    elif name == 'house':
        return "You don't want to go back in the house."
    elif name == 'tree' or name.startswith('tree_'):
        return 'The tree leaves rustle gently in the breeze.'
    elif name == 'key':
        return "It's some sort of key."
    elif name == 'gate':
        return "There's a gate here, but it's locked."
    elif name.startswith('open_gate_'):
        return 'You walk into the gate. Ouch.'
    elif name.startswith('block_'):
        return 'An oversized alphabet block. How curious.'
    elif name == 'billboard_2':
        return 'It\'s a billboard. It says, "Go up."'
    elif name == 'billboard_3':
        return '"Seriously, go up."'
    elif name == 'billboard_4':
        return ('"Roses are red, violets are blue. My billboards are lies, '
                'did I fool you?"')
    elif name == 'bunny_prints':
        return 'What are these tracks?'
    elif name == 'bunny':
        return 'A bunny! Your heart melts.'
    elif name == 'eggplant':
        return 'An eggplant. Ew.'
    elif name == 'trash_can':
        return 'Do you have the eggplant?'
    elif name == 'fishing_rod':
        return 'Who left a fishing rod here?'
    elif name == 'lake':
        return 'What a lovely calm lake.'
    elif name == 'angry_cat':
        return 'Your way is blocked by an angry cat.'
    elif name == 'happy_cat':
        return 'The well-fed cat purrs when you pet it.'
    elif name == 'bucket':
        return 'You wonder why random stuff is scattered all over the place.'
    elif name == 'matches':
        return 'Ooh, matches.'
    elif name == 'doll':
        return "It's a worn cloth doll with button eyes and yarn hair."
    elif name == 'shrubbery':
        return 'Your way is blocked by a shrubbery.'
    elif name == 'fire':
        return 'Your way is blocked by a flaming shrubbery.'
    elif name == 'hole':
        return "It's a hole in the ground."
    elif name == 'billboard_16':
        return '"Go down."'
    elif name == 'billboard_10':
        return ('"Roses are red, violets are blue. Believe it or not, I '
                'sometimes tell the truth =P"')
    elif name.startswith('flowers_'):
        return 'The sweet scent of wildflowers makes your nose itch.'
    else:
        raise NotImplementedError(f'Collided with {name}')


def collide(speed, name) -> Collision:
    return Collision(speed, _collision_reason(name))


def _simple_obtain_effects(name):
    return [(Effect.add_item(name),), (Effect.remove_object(name),)]


def obtain(name) -> Optional[Item]:
    if name.startswith('tree_'):
        fruit = name[len('tree_'):]
        return Item((Effect.add_item(fruit),), (), f'You pick a ripe {fruit}.')
    elif name == 'key':
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
    elif name == 'bucket':
        return Item(*_simple_obtain_effects(name), 'Finders keepers, right?')
    elif name == 'matches':
        return Item(*_simple_obtain_effects(name),
                    'You never know what you may want to set on fire.')
    elif name == 'hole':
        return Item(
            (), (),
            'You fall into the hole and climb back out. You feel foolish.')
    else:
        return None


def use(name) -> Sequence[Use]:
    if name in ('peach', 'apple'):
        return [Use(None, (Effect.remove_item(name),), (),
                    f'You eat the {name}. Yum.')]
    elif name == 'key':
        object_effects = (Effect.remove_object('gate'),
                          Effect.add_object('open_gate_left'),
                          Effect.add_object('open_gate_right'))
        return [Use('gate', (Effect.remove_item('key'),), object_effects,
                    'You unlock the gate.')]
    elif name.startswith('block_'):
        return []
    elif name == 'eggplant':
        return [
            Use('angry_cat', (Effect.remove_item('eggplant'),), (),
                'You feed the cat the eggplant. The cat is even angrier now.'),
            Use('trash_can', (Effect.remove_item('eggplant'),), (),
                "Yeah, you don't need that.")]
    elif name == 'fishing_rod':
        item_effects = (Effect.remove_item('fishing_rod'),
                        Effect.add_item('fish'))
        return [
            Use('lake', item_effects, (), "You catch a tasty-looking fish.")]
    elif name == 'fish':
        object_effects = (Effect.remove_object('angry_cat'),
                          Effect.add_object('happy_cat'))
        return [Use('angry_cat', (Effect.remove_item('fish'),), object_effects,
                    'You feed the cat the fish. The cat is happy.')]
    elif name == 'bucket':
        item_effects = (Effect.remove_item('bucket'),
                        Effect.add_item('filled_bucket'))
        return [Use('lake', item_effects, (),
                    'You fill the bucket with lake water.')]
    elif name == 'filled_bucket':
        object_effects = (Effect.remove_object('shrubbery'),
                          Effect.remove_object('fire'))
        return [Use(
            'fire', (Effect.remove_item('filled_bucket'),), object_effects,
            'You put out the fire. The shrubbery has been burned down.')]
    elif name == 'matches':
        return [
            Use('doll', (), (Effect.remove_object('doll'),),
                'You burn the well-loved doll to ashes. You monster.'),
            Use('shrubbery', (Effect.remove_item('matches'),),
                (Effect.add_object('fire'),),
                'Your way is now blocked by a flaming shrubbery.')]
    else:
        raise NotImplementedError(f'Used {name}')
