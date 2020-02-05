"""Tests for maze.state."""

from pygame.locals import *
import unittest

from common import test_utils
from maze import play_area
from maze import state
from maze import walls


class ShortEscapeEndingTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.ending = state.ShortEscapeEnding(self.screen)

    def test_tick_to_active(self):
        self.ending.active = True
        self.ending._frame = 1
        self.ending.handle_tick(
            test_utils.MockEvent(state.ShortEscapeEnding._TICK))
        self.assertTrue(self.ending.active)

    def test_tick_to_inactive(self):
        self.ending.active = True
        self.ending._frame = 2
        self.ending.handle_tick(
            test_utils.MockEvent(state.ShortEscapeEnding._TICK))
        self.assertFalse(self.ending.active)


class GameTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.game = state.Game(self.screen)

    def test_draw(self):
        self.game.draw()

    def test_start_player_movement(self):
        self.assertTrue(self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT)))
        self.assertFalse(self.game._side_bar.text_area._text)

    def test_end_player_movement(self):
        self.assertTrue(self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYUP, key=K_LEFT)))

    def test_tick(self):
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_UP))
        self.assertTrue(self.game.handle_player_movement(
            test_utils.MockEvent(typ=play_area.TICK)))
        self.assertFalse(self.game._side_bar.text_area._text)

    def test_player_collision(self):
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_UP))
        # Since the player is standing with his head overlapping with the house,
        # this speed should result in a collision.
        self.game._play_area._scroll_speed = (
            0, self.game._play_area.player.RECT.h)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=play_area.TICK))
        self.assertTrue(self.game._side_bar.text_area._text)

    def test_movement_unrelated_event(self):
        self.assertFalse(self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_r)))

    def test_current_square(self):
        self.assertEqual(self.game._side_bar.mini_map._current_square, (0, 0))
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT))
        self.assertEqual(self.game._side_bar.mini_map._current_square, (0, 0))
        self.game._play_area._scroll_speed = (800, 0)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=play_area.TICK))
        self.assertEqual(self.game._side_bar.mini_map._current_square, (-1, 0))

    def test_seen_walls(self):
        self.assertFalse(self.game._side_bar.mini_map._seen_walls)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_RIGHT))
        self.assertFalse(self.game._side_bar.mini_map._seen_walls)
        self.game._play_area._scroll_speed = (-200, 0)
        for _ in range(2):
            self.game.handle_player_movement(
                test_utils.MockEvent(typ=play_area.TICK))
        wall, = self.game._side_bar.mini_map._seen_walls
        self.assertEqual(wall.SQUARE, (0, 0))
        self.assertEqual(wall.SIDE, walls.Side.RIGHT)


if __name__ == '__main__':
    unittest.main()
