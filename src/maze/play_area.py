"""Gameplay area."""

import abc
import pygame
from pygame.locals import *
from typing import Callable, Mapping

from common import color
from common import img
from common import state
from . import objects

TICK = pygame.USEREVENT
TICK_INTERVAL_MS = 100
# We scroll the background instead of moving the player.
_PLAYER_MOVES = {
    K_LEFT: (5, 0), K_RIGHT: (-5, 0), K_UP: (0, 5), K_DOWN: (0, -5)}


# pytype: disable=ignored-abstractmethod
class _MovableFactory(img.RectFactory):

    @abc.abstractmethod
    def move(self, delta):
        pass
# pytype: enable=ignored-abstractmethod


class _MovablePngFactory(img.PngFactory, _MovableFactory):

    def move(self, delta):
        self._pos = (self._pos[0] + delta[0], self._pos[1] + delta[1])
        self.RECT = pygame.Rect(self._pos, self._img.get_size())


def _load(name, *args, **kwargs):
    return lambda screen: _MovablePngFactory(name, screen, *args, **kwargs)


class Surface(objects.Surface):
    """A subsurface with movable objects on it."""

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)
    # We don't include the player here because he is a special fixed object.
    OBJECTS: Mapping[str, Callable[[pygame.Surface], _MovableFactory]] = {
        'house': _load('house', (150, -130))}

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

    def handle_player_movement(self, event):
        if event.type == KEYUP and event.key in _PLAYER_MOVES:
            self._scroll_speed = None
            return True
        elif event.type == KEYDOWN and event.key in _PLAYER_MOVES:
            self._scroll_speed = _PLAYER_MOVES[event.key]
        elif event.type != TICK or not self._scroll_speed:
            return False
        for name, obj in self._objects.items():
            obj.move(self._scroll_speed)
        return True
