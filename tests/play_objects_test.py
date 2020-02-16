"""Tests for maze.play_objects."""

import pygame
import unittest

from common import test_utils
from maze import play_objects


class HouseTest(test_utils.ImgTestCase):

    def setUp(self):
        super().setUp()
        self.house = play_objects.House(self.screen)

    def test_colliderect(self):
        self.assertTrue(self.house.RECT.colliderect(
            pygame.Rect(self.house.RECT.center, (10, 10))))

    def test_nocolliderect(self):
        self.assertFalse(self.house.RECT.colliderect(
            pygame.Rect(self.house.RECT.topleft, (10, 10))))


class OpenGateTest(test_utils.GameStateTestCase):

    def test_draw(self):
        play_objects.OpenGateLeft(self.screen).draw()
        play_objects.OpenGateRight(self.screen).draw()


class FishingRodTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.fishing_rod = play_objects.FishingRod(self.screen)

    def test_colliderect(self):
        self.assertTrue(self.fishing_rod.RECT.colliderect(
            pygame.Rect(self.fishing_rod.RECT.center, (10, 10))))

    def test_nocolliderect(self):
        self.assertFalse(self.fishing_rod.RECT.colliderect(
            pygame.Rect(self.fishing_rod.RECT.topleft, (10, 10))))

    def test_collidepoint(self):
        self.assertTrue(self.fishing_rod.collidepoint(
            self.fishing_rod.RECT.center))

    def test_nocollidepoint(self):
        self.assertFalse(self.fishing_rod.collidepoint(
            self.fishing_rod.RECT.topleft))

    def test_draw(self):
        self.fishing_rod.draw()


class LakeTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.lake = play_objects.Lake(self.screen)

    def test_colliderect(self):
        self.assertTrue(self.lake.RECT.colliderect(
            pygame.Rect(self.lake.RECT.center, (10, 10))))

    def test_nocolliderect(self):
        self.assertFalse(self.lake.RECT.colliderect(
            pygame.Rect(self.lake.RECT.topleft, (10, 10))))

    def test_draw(self):
        self.lake.draw()


class HoleTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.hole = play_objects.Hole(self.screen)

    def test_colliderect(self):
        self.assertTrue(self.hole.RECT.colliderect(
            pygame.Rect(self.hole.RECT.center, (10, 10))))

    def test_nocolliderect(self):
        self.assertFalse(self.hole.RECT.colliderect(
            pygame.Rect(self.hole.RECT.topleft, (10, 10))))

    def test_collidepoint(self):
        self.assertTrue(self.hole.RECT.collidepoint(self.hole.RECT.center))

    def test_nocollidepoint(self):
        self.assertFalse(self.hole.RECT.collidepoint(self.hole.RECT.topleft))

    def test_draw(self):
        self.hole.draw()


if __name__ == '__main__':
    unittest.main()
