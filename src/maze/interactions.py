"""Player interactions."""

import dataclasses
import enum
import itertools
from typing import Optional, Sequence, Set, Tuple, Union
from . import play_objects
from . import walls

Speed = Tuple[int, int]
SquaresType = Union[Set[Tuple[int, int]], 'Squares']
_DEFAULT_INFLATION = (100, 100)


class ItemEffectType(enum.Enum):
    REMOVE = enum.auto()
    ADD = enum.auto()


class ObjectEffectType(enum.Enum):
    REMOVE = enum.auto()
    ADD = enum.auto()
    HIDE = enum.auto()


class StateEffectType(enum.Enum):
    REMOVE = enum.auto()


@dataclasses.dataclass
class Effect:
    type: Union[ItemEffectType, ObjectEffectType, StateEffectType]
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

    @classmethod
    def hide_object(cls, obj):
        return cls(ObjectEffectType.HIDE, obj)

    @classmethod
    def remove_state(cls, state):
        return cls(StateEffectType.REMOVE, state)


@dataclasses.dataclass
class Collision:
    reason: str
    max_nocollision_speed: Optional[Speed]
    play_area_effects: Sequence[Effect] = ()

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


@dataclasses.dataclass
class Item:
    reason: str
    item_effects: Sequence[Effect] = ()
    play_area_effects: Sequence[Effect] = ()


@dataclasses.dataclass
class Use:
    reason: str
    activator: Tuple[str, ...]
    item_effects: Sequence[Effect] = ()
    play_area_effects: Sequence[Effect] = ()


class Squares(enum.Enum):
    DEFAULT = enum.auto()
    ALL = enum.auto()


@dataclasses.dataclass
class _Config:
    # Which squares a player has to be in to interact with an object.
    squares: SquaresType = Squares.DEFAULT
    # How much to inflate the object size when determining whether the player is
    # close enough to interact with it.
    inflation: Tuple[int, int] = _DEFAULT_INFLATION


_Config.DEFAULT = _Config()


def _collision(name) -> Union[str, Tuple[str, Sequence[Effect]]]:
    if walls.match(name) or walls.partial_match(name):
        return "That's a wall..."
    elif name == 'house':
        return "You don't want to go back in the house."
    elif name.startswith('flowers_'):
        return 'The sweet scent of wildflowers makes your nose itch.'
    elif name.startswith('tree_'):
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
    elif name == 'cake':
        return 'A huge chocolate cake!'
    elif name == 'invisible_wall':
        return ('Thinking of the cake, you suddenly crave something sweet.',
                (Effect.remove_state('pre_crave'),))
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
    elif name.startswith('puzzle_') or name.startswith('slotted_block_'):
        return 'This wall looks unusual.'
    else:
        raise NotImplementedError(f'Collided with {name}')


def collide(name, speed) -> Collision:
    result: Union[str, Tuple[str, Sequence[Effect]]] = _collision(name)
    if isinstance(result, str):
        return Collision(result, speed)
    else:
        reason, effects = result
        return Collision(reason, speed, effects)


def _simple_obtain_effects(name):
    return [(Effect.add_item(name),), (Effect.remove_object(name),)]


def obtain(name) -> Optional[Item]:
    if name in (f'tree_{fruit}' for fruit in play_objects.FRUITS):
        fruit = name[len('tree_'):]
        return Item(f'You pick a ripe {fruit}.', (Effect.add_item(fruit),))
    elif name == 'key':
        return Item('You pick up the key.', *_simple_obtain_effects(name))
    elif name.startswith('block_'):
        return Item(
            'You decide to carry the giant wooden block around with you.',
            *_simple_obtain_effects(name))
    elif name == 'eggplant':
        return Item('You gingerly pick up the disgusting vegetable.',
                    *_simple_obtain_effects(name))
    elif name == 'fishing_rod':
        return Item("You steal someone's fishing rod.",
                    *_simple_obtain_effects(name))
    elif name == 'cake':
        return Item('On closer inspection, the cake is made of styrofoam.')
    elif name == 'bucket':
        return Item('Finders keepers, right?', *_simple_obtain_effects(name))
    elif name == 'matches':
        return Item('You never know what you may want to set on fire.',
                    *_simple_obtain_effects(name))
    elif name == 'hole':
        return Item(
            'You fall into the hole and climb back out. You feel foolish.')
    elif name.startswith('slotted_block_'):
        block_char = name[len('slotted_block_')]
        slot_char = name[-1]
        return Item('You pry the block back out of the wall slot.',
                    (Effect.add_item(f'block_{block_char}'),),
                    (Effect.hide_object(name),
                     Effect.add_object(f'puzzle_slot_{slot_char}')))
    else:
        return None


def _use_block(block_char, slot_char):
    block = f'block_{block_char}'
    slot = f'puzzle_slot_{slot_char}'
    slotted_block = f'slotted_{block}_in_{slot_char}'
    activator = (slot,)
    item_effects = (Effect.remove_item(block),)
    play_area_effects = (Effect.hide_object(slot),
                         Effect.add_object(slotted_block))
    if block_char == slot_char:
        solver = activator + ('puzzle_door',) + tuple(
            f'slotted_block_{char}_in_{char}'
            for char in 'LOVE' if char != block_char)
        yield Use(
            'As you slot the block in, you hear a rumbling sound. The middle '
            'of the wall sinks into the ground.', solver, item_effects,
            play_area_effects + (Effect.remove_object('puzzle_door'),))
    yield Use('The block fits perfectly in this slot in the wall.', activator,
              item_effects, play_area_effects)


def use(name) -> Sequence[Use]:
    if name in play_objects.FRUITS:
        item_effects = (Effect.remove_item(name),)
        reason = f'You eat the {name}. '
        return [Use(reason + 'Yum.', ('pre_crave',), item_effects),
                Use(reason + 'Your sweet craving is satisfied.',
                    ('invisible_wall',), item_effects,
                    (Effect.remove_object('invisible_wall'),)),
                Use(reason + 'You feel bloated.', (), item_effects)]
    elif name == 'key':
        play_area_effects = (Effect.remove_object('gate'),
                             Effect.add_object('open_gate_left'),
                             Effect.add_object('open_gate_right'))
        return [Use('You unlock the gate.', ('gate',),
                    (Effect.remove_item('key'),), play_area_effects)]
    elif name.startswith('block_'):
        block_char = name[len('block_'):]
        uses = []
        for slot_char in 'LOVE':
            uses.extend(_use_block(block_char, slot_char))
        return uses
    elif name == 'eggplant':
        return [
            Use('You feed the cat the eggplant. The cat is even angrier now.',
                ('angry_cat',), (Effect.remove_item('eggplant'),)),
            Use("Yeah, you don't need that.", ('trash_can',),
                (Effect.remove_item('eggplant'),))]
    elif name == 'fishing_rod':
        item_effects = (Effect.remove_item('fishing_rod'),
                        Effect.add_item('fish'))
        return [Use("You catch a tasty-looking fish.", ('lake',), item_effects)]
    elif name == 'fish':
        play_area_effects = (Effect.remove_object('angry_cat'),
                             Effect.add_object('happy_cat'))
        return [
            Use('You feed the cat the fish. The cat is happy.', ('angry_cat',),
                (Effect.remove_item('fish'),), play_area_effects)]
    elif name == 'bucket':
        item_effects = (Effect.remove_item('bucket'),
                        Effect.add_item('filled_bucket'))
        return [Use('You fill the bucket with lake water.', ('lake',),
                    item_effects)]
    elif name == 'filled_bucket':
        play_area_effects = (Effect.remove_object('shrubbery'),
                             Effect.remove_object('fire'))
        return [Use('You put out the fire. The shrubbery has been burned down.',
                    ('fire',), (Effect.remove_item('filled_bucket'),),
                    play_area_effects)]
    elif name == 'matches':
        return [
            Use('You burn the well-loved doll to ashes. You monster.',
                ('doll',), play_area_effects=(Effect.remove_object('doll'),)),
            Use('Your way is now blocked by a flaming shrubbery.',
                ('shrubbery',), (Effect.remove_item('matches'),),
                (Effect.add_object('fire'),))]
    else:
        raise NotImplementedError(f'Used {name}')


_CUSTOM_CONFIG = {
    'tree_peach': _Config(squares={(0, 0), (-1, 0), (-1, 1)}),
    'fishing_rod': _Config(squares={(1, 2), (1, 3)}),
    'cake': _Config(squares={(2, 1), (3, 1)}),
    'invisible_wall': _Config(squares=Squares.ALL),
    'shrubbery': _Config(squares={(3, 1), (4, 1)}),
    'fire': _Config(squares={(3, 1), (4, 1)}),
    'puzzle_door': _Config(squares={(2, 3), (2, 4)}, inflation=(360, 175)),
    'puzzle_slot_L': _Config(squares={(2, 3), (2, 4)}, inflation=(-40, 100)),
    'puzzle_slot_O': _Config(squares={(2, 3), (2, 4)}, inflation=(-40, 100)),
    'puzzle_slot_V': _Config(squares={(2, 3), (2, 4)}, inflation=(-40, 100)),
    'puzzle_slot_E': _Config(squares={(2, 3), (2, 4)}, inflation=(-40, 100)),
}


for block_char, slot_char in itertools.product('LOVE', repeat=2):
    inflate_x = 840 if slot_char in 'LE' else 600
    _CUSTOM_CONFIG[f'slotted_block_{block_char}_in_{slot_char}'] = _Config(
        squares={(2, 3), (2, 4)}, inflation=(inflate_x, 100))
del block_char, slot_char, inflate_x


def config(name, attr):
    return getattr(_CUSTOM_CONFIG.get(name, _Config.DEFAULT), attr)
