"""Base classes for game objects."""

import pygame
from typing import Callable, Mapping, Tuple

from common import img

ObjectsType = Mapping[str, Callable[[pygame.Surface], img.RectFactory]]


class Rect(img.RectFactory):
    """A colored, drawable rectangle."""

    COLOR: Tuple[int, int, int]

    def draw(self):
        pygame.draw.rect(self._screen, self.COLOR, self.RECT)


class Surface(img.RectFactory):
    """A subsurface with objects on it."""

    OBJECTS: ObjectsType = {}

    def __init__(self, screen):
        super().__init__(screen)
        self._surface = screen.subsurface(self.RECT)
        self._objects = {name: cls(self._surface)
                         for name, cls in self.OBJECTS.items()}

    def __getattr__(self, name):
        if name in self._objects:
            return self._objects[name]
        return self.__getattribute__(name)

    def _visible(self, obj):
        return obj.RECT.colliderect(self._surface.get_rect())

    def draw(self):
        for obj in self._objects.values():
            if self._visible(obj):
                obj.draw()
