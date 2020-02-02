"""Base classes for game objects."""

import pygame
from typing import Callable, Mapping, Tuple

from common import img


class _Object(img.Factory):
    """A drawable object bounded by a rectangle."""

    RECT: pygame.Rect

    def collidepoint(self, pos):
        return self.RECT.collidepoint(pos)


class Rect(_Object):
    """A colored, drawable rectangle."""

    COLOR: Tuple[int, int, int]

    def draw(self):
        pygame.draw.rect(self._screen, self.COLOR, self.RECT)


def Image(name, **kwargs):
    """A png image that can be placed on a Surface."""
    return lambda screen: img.load(name, screen=screen, **kwargs)


class Surface(_Object):
    """A subsurface with objects on it."""

    OBJECTS: Mapping[str, Callable[[pygame.Surface], img.Factory]] = {}

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
            obj.draw()
