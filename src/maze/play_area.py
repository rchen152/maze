"""Gameplay area."""

import itertools
import pygame
from pygame.locals import *
from typing import Optional, Union

from common import color
from common import img
from common import state
from . import interactions
from . import objects
from . import play_map
from . import walls

_TICK = pygame.USEREVENT
_TICK_INTERVAL_MS = 100
_PLAYER_SPEED_INTERVAL = 5
# We scroll the background instead of moving the player.
_PLAYER_MOVES = {
    K_LEFT: (_PLAYER_SPEED_INTERVAL, 0), K_RIGHT: (-_PLAYER_SPEED_INTERVAL, 0),
    K_UP: (0, _PLAYER_SPEED_INTERVAL), K_DOWN: (0, -_PLAYER_SPEED_INTERVAL)}
_PLAYER_FEET_HEIGHT = 15
_OPEN_GATE_SIZE = (5, 82)


def _load(name, *args, **kwargs):
    return lambda screen: img.PngFactory(name, screen, *args, **kwargs)


def _shift_pos(pos, shift):
    return tuple(pos[i] + shift[i] for i in range(2))


def _shift_speed(speed, direction):
    return tuple(s + direction * _PLAYER_SPEED_INTERVAL * s / abs(s) if s else s
                 for s in speed)


def _decelerate(speed):
    speed = _shift_speed(speed, -1)
    return None if speed == (0, 0) else speed


def _accelerate(speed):
    return _shift_speed(speed, 1)


class OpenGateLeft(objects.Rect):

    RECT = pygame.Rect(
        _shift_pos(play_map.square_to_pos(0, 0), (316, -_OPEN_GATE_SIZE[1])),
        _OPEN_GATE_SIZE)
    COLOR = color.BROWN


class OpenGateRight(objects.Rect):

    RECT = pygame.Rect(
        _shift_pos(play_map.square_to_pos(1, 0), (-320, -_OPEN_GATE_SIZE[1])),
        _OPEN_GATE_SIZE)
    COLOR = color.BROWN


class Surface(objects.Surface):
    """A subsurface with movable objects on it."""

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)
    # We don't include the player here because he is a special fixed object.
    OBJECTS = {
        **walls.ALL,
        'house': _load('house', play_map.HOUSE_POS),
        'partial_wall_gateleft': _load(
            'partial_wall_horizontal', play_map.square_to_pos(0, 0), (0, -0.5)),
        'partial_wall_gateright': _load(
            'partial_wall_horizontal', play_map.square_to_pos(1, 0),
            (-1, -0.5)),
        'gate': _load(
            'gate', _shift_pos(
                play_map.square_to_pos(0, 0), (play_map.SQUARE_LENGTH / 2, 15)),
            (-0.5, -1)),
        'key': _load(
            'key', _shift_pos(play_map.square_to_pos(-1, 1), (150, 600))),
    }
    _HIDDEN_OBJECTS = {
        'open_gate_left': OpenGateLeft,
        'open_gate_right': OpenGateRight,
    }

    def __init__(self, screen):
        super().__init__(screen)
        self._hidden_objects = {name: cls(self._surface)
                                for name, cls in self._HIDDEN_OBJECTS.items()}
        self.player = img.load('player', self._surface,
                               (state.RECT.h / 2, state.RECT.h / 2),
                               (-0.5, -0.5))
        self._scroll_speed = None
        self._player_feet_rect = pygame.Rect(
            self.player.RECT.x, self.player.RECT.bottom - _PLAYER_FEET_HEIGHT,
            self.player.RECT.w, _PLAYER_FEET_HEIGHT)

    def _square(self, rect):
        return play_map.pos_to_square(
            rect.move(tuple(play_map.HOUSE_POS[i] - self.house.RECT.topleft[i]
                            for i in range(2))).midbottom)

    @property
    def current_square(self):
        return self._square(self._player_feet_rect)

    @property
    def visible_walls(self):
        return {wall for name, wall in self._objects.items()
                if walls.match(name) and self._visible(wall) and
                self.current_square in wall.adjacent_squares}

    def draw(self):
        self._surface.fill(color.BLUE)
        super().draw()
        self.player.draw()

    def check_player_collision(self) -> Optional[interactions.Collision]:
        # Check if the player's feet would hit anything if he took a step
        # against the background scroll direction.

        def _get_player_path_rect(speed):
            next_feet_rect = self._player_feet_rect.move(
                tuple(-s for s in speed))
            return self._player_feet_rect.union(next_feet_rect)

        player_path_rect = _get_player_path_rect(self._scroll_speed)
        closest_collision = None
        for name, obj in self._objects.items():
            if player_path_rect.colliderect(obj.RECT):
                # Find the maximum speed at which the player won't collide.
                speed = _decelerate(self._scroll_speed)
                while speed:
                    if not _get_player_path_rect(speed).colliderect(obj.RECT):
                        break
                    speed = _decelerate(speed)
                if closest_collision and closest_collision.closer_than(speed):
                    continue
                closest_collision = interactions.collide(speed, name)
        return closest_collision

    def handle_player_movement(self, event) -> Union[bool, str]:
        if event.type == KEYUP and event.key in _PLAYER_MOVES:
            self._scroll_speed = None
            pygame.time.set_timer(_TICK, 0)
            return True
        elif event.type == KEYDOWN and event.key in _PLAYER_MOVES:
            self._scroll_speed = _PLAYER_MOVES[event.key]
            pygame.time.set_timer(_TICK, _TICK_INTERVAL_MS)
        elif event.type == _TICK:
            if not self._scroll_speed:
                # The player has been stopped by an obstacle.
                return True
            self._scroll_speed = _accelerate(self._scroll_speed)
        else:
            return False
        collision = self.check_player_collision()
        if collision:
            # Move the player as close to the obstacle as possible.
            speed = collision.max_nocollision_speed
            move_result = collision.reason
            self._scroll_speed = None
        else:
            speed = self._scroll_speed
            move_result = True
        if speed:
            for obj in itertools.chain(self._objects.values(),
                                       self._hidden_objects.values()):
                obj.move(speed)
        return move_result

    def _player_close_to(self, rect):
        if self.current_square != self._square(rect):
            return False
        return self.player.RECT.colliderect(rect.inflate(rect.w, rect.h))

    def handle_click(self, pos) -> Union[bool, interactions.Item]:
        if not self.collidepoint(pos):
            return False
        for name in ('key',):
            if name not in self._objects:
                continue
            item = self._objects[name]
            if item.collidepoint(pos) and self._player_close_to(item.RECT):
                del self._objects[name]
                return interactions.pick_up(name)
        return True

    def use_item(self, name) -> Optional[str]:
        use = interactions.use(name)
        if not self._player_close_to(self._objects[use.name].RECT):
            return None
        del self._objects[use.name]
        for effect in use.effects:
            self._objects[effect] = self._hidden_objects[effect]
            del self._hidden_objects[effect]
        return use.reason
