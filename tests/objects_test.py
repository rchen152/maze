"""Tests for maze.objects."""

import pygame
import unittest

from common import test_utils
from maze import objects


class BaseTest(unittest.TestCase):

    class TestObject(objects.Base):
        RECT = pygame.Rect(1, 1, 10, 10)

        def draw(self):
            pass

    def setUp(self):
        super().setUp()
        self.obj = self.TestObject(test_utils.MockScreen())

    def test_collidepoint(self):
        self.assertTrue(self.obj.collidepoint((5, 5)))

    def test_nocollidepoint(self):
        self.assertFalse(self.obj.collidepoint((0, 0)))


class SurfaceTest(test_utils.GameStateTestCase):

    class TestSurface(objects.Surface):

        class MockRect:

            def __init__(self, unused_screen):
                self.drawn = 0

            def draw(self):
                self.drawn += 1

        RECT = pygame.Rect((1, 1, 10, 10))
        OBJECTS = {'mock_rect': MockRect}

    def setUp(self):
        super().setUp()
        self.surface = self.TestSurface(self.screen)

    def test_collidepoint(self):
        self.assertTrue(self.surface.collidepoint((5, 5)))

    def test_nocollidepoint(self):
        self.assertFalse(self.surface.collidepoint((0, 0)))

    def test_draw(self):
        self.surface.draw()
        self.assertEqual(self.surface.mock_rect.drawn, 1)


if __name__ == '__main__':
    unittest.main()
