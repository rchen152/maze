"""Gameplay area."""

import pygame

from common import color
from common import state
from . import objects


class Surface(objects.Surface):

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)
    OBJECTS = {'house': objects.Image('house', position=(150, -130)),
               'player': objects.Image(
                   'player',
                   position=(state.RECT.h / 2, state.RECT.h / 2),
                   shift=(-0.5, -0.5))}

    def __init__(self, screen):
        super().__init__(screen)
        self._surface.fill(color.BLUE)
