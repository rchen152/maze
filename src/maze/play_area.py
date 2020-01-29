"""Gameplay area."""

import pygame

from common import color
from common import state
from . import objects


class Surface(objects.Surface):

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)

    def __init__(self, screen):
        super().__init__(screen)
        self._surface.fill(color.BLUE)
