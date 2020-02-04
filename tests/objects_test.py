"""Tests for maze.objects."""

import pygame
import unittest

from common import img
from common import test_utils
from maze import objects


class MovablePngTest(test_utils.ImgTestCase):

    def test_move(self):
        obj = objects.MovablePngFactory(
            'title_card', self.screen, path_type=img.PathType.COMMON)
        pos = obj.RECT.topleft
        obj.move((1, 1))
        self.assertEqual(obj.RECT.topleft, (pos[0] + 1, pos[1] + 1))

    def test_load(self):
        factory = objects.load_movable_png(
            'title_card', path_type=img.PathType.COMMON)
        self.assertIsInstance(factory(self.screen), objects.MovablePngFactory)


class SurfaceTest(test_utils.GameStateTestCase):

    class TestSurface(objects.Surface):

        class CollidingMockRect(img.RectFactory):
            RECT = pygame.Rect(0, 0, 1, 1)

            def __init__(self, unused_screen):
                self.drawn = 0

            def draw(self):
                self.drawn += 1

        class NoCollidingMockRect(img.RectFactory):
            RECT = pygame.Rect(10, 10, 1, 1)

            def __init__(self, unused_screen):
                self.drawn = 0

            def draw(self):
                self.drawn += 1

        RECT = pygame.Rect((1, 1, 10, 10))
        OBJECTS = {'colliding_mock_rect': CollidingMockRect,
                   'nocolliding_mock_rect': NoCollidingMockRect}

    def setUp(self):
        super().setUp()
        self.surface = self.TestSurface(self.screen)

    def test_collidepoint(self):
        self.assertTrue(self.surface.collidepoint((5, 5)))

    def test_nocollidepoint(self):
        self.assertFalse(self.surface.collidepoint((0, 0)))

    def test_draw(self):
        self.surface.draw()
        self.assertEqual(self.surface.colliding_mock_rect.drawn, 1)
        self.assertEqual(self.surface.nocolliding_mock_rect.drawn, 0)


if __name__ == '__main__':
    unittest.main()
