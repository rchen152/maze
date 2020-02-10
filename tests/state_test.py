"""Tests for maze.state."""

from pygame.locals import *
import unittest

from common import color
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
        self.assertTrue(self.game._side_bar.text_area._text)
        self.assertTrue(self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT)))
        self.assertFalse(self.game._side_bar.text_area._text)

    def test_end_player_movement(self):
        self.assertTrue(self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYUP, key=K_LEFT)))

    def test_tick(self):
        self.assertTrue(self.game._side_bar.text_area._text)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_UP))
        self.assertTrue(self.game.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK)))
        self.assertFalse(self.game._side_bar.text_area._text)

    def test_player_collision(self):
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_UP))
        # Since the player is standing with his head overlapping with the house,
        # this speed should result in a collision.
        self.game._play_area._scroll_speed = (
            0, self.game._play_area.player.RECT.h)
        self.assertFalse(self.game._side_bar.text_area._text)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK))
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
            test_utils.MockEvent(typ=play_area._TICK))
        self.assertEqual(self.game._side_bar.mini_map._current_square, (-1, 0))

    def test_seen_walls(self):
        self.assertFalse(self.game._side_bar.mini_map._seen_walls)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_RIGHT))
        self.assertFalse(self.game._side_bar.mini_map._seen_walls)
        self.game._play_area._scroll_speed = (-400, 0)
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK))
        wall, = self.game._side_bar.mini_map._seen_walls
        self.assertEqual(wall.SQUARE, (0, 0))
        self.assertEqual(wall.SIDE, walls.Side.RIGHT)

    def test_turn_minimap_red(self):
        self.assertNotEqual(
            self.game._side_bar.mini_map._square_color, color.RED)
        for obj in self.game._play_area._objects.values():
            obj.move((-1600, -3200))
        self.game.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_DOWN))
        self.assertEqual(self.game._side_bar.mini_map._square_color, color.RED)

    def test_non_click(self):
        self.assertFalse(
            self.game.handle_click(test_utils.MockEvent(typ=MOUSEBUTTONUP)))

    def test_click(self):
        self.assertTrue(self.game.handle_click(
            test_utils.MockEvent(typ=MOUSEBUTTONDOWN, button=1, pos=(0, 0))))

    def test_click_key(self):
        for obj in self.game._play_area._objects.values():
            obj.move((950, -950))
        self.game._side_bar.text_area.show(None)
        self.assertTrue(self.game.handle_click(
            test_utils.MockEvent(typ=MOUSEBUTTONDOWN, button=1,
                                 pos=self.game._play_area.key.RECT.center)))
        self.assertNotIn('key', self.game._play_area._objects)
        self.assertEqual(self.game._side_bar.item_cell0.item, 'key')
        self.assertTrue(self.game._side_bar.text_area._text)

    def test_use_key(self):
        del self.game._play_area._objects['key']
        self.game._side_bar.add_item('key')
        for obj in self.game._play_area._objects.values():
            obj.move((0, 480))
        self.game._side_bar.text_area.show(None)
        self.assertTrue(self.game.handle_click(
            test_utils.MockEvent(
                typ=MOUSEBUTTONDOWN, button=1,
                pos=self.game._side_bar.item_cell0.RECT.move((576, 0)).center)))
        self.assertNotIn('gate', self.game._play_area._objects)
        self.assertIsNone(self.game._side_bar.item_cell0.item)
        self.assertTrue(self.game._side_bar.text_area._text)

    def test_fail_use_key(self):
        del self.game._play_area._objects['key']
        self.game._side_bar.add_item('key')
        self.game._side_bar.text_area.show(None)
        self.assertTrue(self.game.handle_click(
            test_utils.MockEvent(
                typ=MOUSEBUTTONDOWN, button=1,
                pos=self.game._side_bar.item_cell0.RECT.move((576, 0)).center)))
        self.assertIn('gate', self.game._play_area._objects)
        self.assertIsNotNone(self.game._side_bar.item_cell0.item)
        self.assertTrue(self.game._side_bar.text_area._text)


if __name__ == '__main__':
    unittest.main()
