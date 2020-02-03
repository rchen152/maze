"""Tests for maze.play_area."""

from pygame.locals import *
import unittest

from common import test_utils
from maze import play_area


class SurfaceTest(test_utils.ImgTestCase):

    def setUp(self):
        super().setUp()
        self.play_area = play_area.Surface(self.screen)

    def _set_speed_for_collision(self):
        # Since the player is standing with his head overlapping with the house,
        # this speed should result in a collision.
        self.play_area._scroll_speed = (0, self.play_area.player.RECT.h)

    def test_move(self):
        house_rect = self.play_area.house.RECT
        self.play_area.house.move((1, 1))
        self.assertEqual(self.play_area.house.RECT.topleft,
                         (house_rect.x + 1, house_rect.y + 1))

    def test_check_player_collision(self):
        self._set_speed_for_collision()
        self.assertTrue(self.play_area.check_player_collision())

    def test_check_player_nocollision(self):
        self.play_area._scroll_speed = (0, 0)
        self.assertFalse(self.play_area.check_player_collision())

    def test_start_player_movement(self):
        self.assertIs(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT)), True)
        self.assertGreater(self.play_area._scroll_speed[0], 0)
        self.assertFalse(self.play_area._scroll_speed[1])

    def test_stop_player_movement(self):
        self.assertIs(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYUP, key=K_LEFT)), True)
        self.assertIsNone(self.play_area._scroll_speed)

    def test_tick(self):
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT))
        delta_x = self.play_area._scroll_speed[0]
        self.assertIs(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area.TICK)), True)
        self.assertGreater(self.play_area._scroll_speed[0], delta_x)

    def test_handle_player_collision(self):
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_UP))
        self._set_speed_for_collision()
        self.assertIsInstance(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area.TICK)), str)


if __name__ == '__main__':
    unittest.main()
