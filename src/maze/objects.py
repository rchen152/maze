"""Base classes for game objects."""

import pygame
from typing import Callable, Mapping

from common import img


class MovablePngFactory(img.PngFactory):

    def move(self, delta):
        self.RECT = self.RECT.move(delta)


class Surface(img.RectFactory):
    """A subsurface with objects on it."""

    OBJECTS: Mapping[str, Callable[[pygame.Surface], img.RectFactory]] = {}

    def __init__(self, screen):
        super().__init__(screen)
        self._surface = screen.subsurface(self.RECT)
        self._objects = {name: cls(self._surface)
                         for name, cls in self.OBJECTS.items()}

    def __getattr__(self, name):
        if name in self._objects:
            return self._objects[name]
        return super().__getattr__(name)

    def draw(self):
        for obj in self._objects.values():
            if obj.RECT.colliderect(self._surface.get_rect()):
                obj.draw()
