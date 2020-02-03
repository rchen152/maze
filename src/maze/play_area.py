"""Gameplay area."""

import pygame
from pygame.locals import *
from typing import Callable, Mapping, NamedTuple, Optional, Tuple, Union

from common import color
from common import img
from common import state
from . import objects

TICK = pygame.USEREVENT
TICK_INTERVAL_MS = 100
_PLAYER_SPEED_INTERVAL = 5
# We scroll the background instead of moving the player.
_PLAYER_MOVES = {
    K_LEFT: (_PLAYER_SPEED_INTERVAL, 0), K_RIGHT: (-_PLAYER_SPEED_INTERVAL, 0),
    K_UP: (0, _PLAYER_SPEED_INTERVAL), K_DOWN: (0, -_PLAYER_SPEED_INTERVAL)}
_PLAYER_FEET_HEIGHT = 15


class _MovablePngFactory(img.PngFactory):

    def move(self, delta):
        self.RECT = self.RECT.move(delta)


def _load(name, *args, **kwargs):
    return lambda screen: _MovablePngFactory(name, screen, *args, **kwargs)


def _shift_speed(speed, direction):
    return tuple(s + direction * _PLAYER_SPEED_INTERVAL * s / abs(s) if s else s
                 for s in speed)


def _decelerate(speed):
    speed = _shift_speed(speed, -1)
    return None if speed == (0, 0) else speed


def _accelerate(speed):
    return _shift_speed(speed, 1)


class _Collision(NamedTuple):
    max_nocollision_speed: Optional[Tuple[int, int]]
    reason: str


class Surface(objects.Surface):
    """A subsurface with movable objects on it."""

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)
    # We don't include the player here because he is a special fixed object.
    OBJECTS: Mapping[str, Callable[[pygame.Surface], _MovablePngFactory]] = {
        'house': _load('house', (150, -130)),
        'wall_1right': _load('wall_vertical', (750, -200), (-0.5, 0)),
        'wall_1bottom': _load('wall_horizontal', (-50, 600), (0, -0.5)),
    }

    def __init__(self, screen):
        super().__init__(screen)
        self.player = img.load('player', self._surface,
                               (state.RECT.h / 2, state.RECT.h / 2),
                               (-0.5, -0.5))
        self._scroll_speed = None

    def draw(self):
        self._surface.fill(color.BLUE)
        super().draw()
        self.player.draw()

    def check_player_collision(self) -> Optional[_Collision]:
        # Check if the player's feet would hit anything if he took a step
        # against the background scroll direction.
        current_feet_rect = pygame.Rect(
            self.player.RECT.x, self.player.RECT.bottom - _PLAYER_FEET_HEIGHT,
            self.player.RECT.w, _PLAYER_FEET_HEIGHT)

        def _get_player_path_rect(speed):
            next_feet_rect = current_feet_rect.move(tuple(-s for s in speed))
            return current_feet_rect.union(next_feet_rect)

        player_path_rect = _get_player_path_rect(self._scroll_speed)
        for name, obj in self._objects.items():
            if player_path_rect.colliderect(obj.RECT):
                # Find the maximum speed at which the player won't collide.
                speed = _decelerate(self._scroll_speed)
                while speed:
                    if not _get_player_path_rect(speed).colliderect(obj.RECT):
                        break
                    speed = _decelerate(speed)
                if name == 'house':
                    reason = "You don't want to go back in the house."
                elif name.startswith('wall'):
                    reason = "That's a wall..."
                else:
                    raise NotImplementedError(f'Collided with {name}')
                return _Collision(speed, reason)
        return None

    def handle_player_movement(self, event) -> Union[bool, str]:
        if event.type == KEYUP and event.key in _PLAYER_MOVES:
            self._scroll_speed = None
            pygame.time.set_timer(TICK, 0)
            return True
        elif event.type == KEYDOWN and event.key in _PLAYER_MOVES:
            self._scroll_speed = _PLAYER_MOVES[event.key]
            pygame.time.set_timer(TICK, TICK_INTERVAL_MS)
        elif event.type == TICK:
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
            for name, obj in self._objects.items():
                obj.move(speed)
        return move_result
