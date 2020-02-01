"""Gameplay area."""

import pygame

from common import color
from common import img
from common import state
from . import objects


class Player(img.PngFactory):

    def __init__(self, screen):
        super().__init__('player', screen, (state.RECT.h / 2, state.RECT.h / 2),
                         (-0.5, -0.5))


class Surface(objects.Surface):

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)
    OBJECTS = (Player,)

    def __init__(self, screen):
        super().__init__(screen)
        self._surface.fill(color.BLUE)
