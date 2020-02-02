"""Tests for maze.objects."""

import pygame
import unittest

from common import test_utils
from maze import objects


class RectTest(test_utils.GameStateTestCase):

    class TestRect(objects.Rect):
        RECT = pygame.Rect(1, 1, 10, 10)
        COLOR = (0, 0, 0)

    def setUp(self):
        super().setUp()
        self.rect = self.TestRect(self.screen)

    def test_collidepoint(self):
        self.assertTrue(self.rect.collidepoint((5, 5)))

    def test_nocollidepoint(self):
        self.assertFalse(self.rect.collidepoint((0, 0)))

    def test_draw(self):
        self.rect.draw()


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
