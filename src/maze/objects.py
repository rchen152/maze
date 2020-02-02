"""Base classes for game objects."""

import pygame
from typing import Callable, Sequence, Tuple

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

    OBJECTS: Sequence[Callable[[pygame.Surface], img.Factory]] = ()

    def __init__(self, screen):
        super().__init__(screen)
        self._surface = screen.subsurface(self.RECT)
        self._objects = [cls(self._surface) for cls in self.OBJECTS]

    def draw(self):
        for obj in self._objects:
            obj.draw()
