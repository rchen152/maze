"""Gameplay area."""

import pygame
from pygame.locals import *
from typing import Callable, Mapping, Optional, Union

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

    def check_player_collision(self) -> Optional[str]:
        # Check if the player's feet would hit anything if he took a step
        # against the background scroll direction.
        current_feet_rect = pygame.Rect(
            self.player.RECT.x, self.player.RECT.bottom - _PLAYER_FEET_HEIGHT,
            self.player.RECT.w, _PLAYER_FEET_HEIGHT)
        next_feet_rect = current_feet_rect.move(
            tuple(-s for s in self._scroll_speed))
        player_path_rect = current_feet_rect.union(next_feet_rect)
        for name, obj in self._objects.items():
            if player_path_rect.colliderect(obj.RECT):
                if name == 'house':
                    return "You don't want to go back in the house."
                elif name.startswith('wall'):
                    return "That's a wall..."
                else:
                    raise NotImplementedError(f'Collided with {name}')
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
            assert self._scroll_speed  # for pytype
            self._scroll_speed = tuple(
                s + _PLAYER_SPEED_INTERVAL * s / abs(s) if s else s
                for s in self._scroll_speed)
        else:
            return False
        collision_reason = self.check_player_collision()
        if collision_reason:
            return collision_reason
        for name, obj in self._objects.items():
            obj.move(self._scroll_speed)
        return True
