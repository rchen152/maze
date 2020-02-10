"""Tests for maze.play_area."""

import itertools
from pygame.locals import *
from typing import cast
import unittest

from common import test_utils
from maze import interactions
from maze import play_area
from maze import walls


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

    def test_wall(self):
        # This speed should collide the player with the wall below him.
        self.play_area._scroll_speed = (0, -400)
        self.assertTrue(self.play_area.check_player_collision())

    def test_start_player_movement(self):
        object_x = self.play_area.house.RECT.x
        hidden_object_x = (
            self.play_area._hidden_objects['open_gate_left'].RECT.x)
        self.assertIs(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT)), True)
        speed_x, speed_y = self.play_area._scroll_speed
        self.assertGreater(speed_x, 0)
        self.assertFalse(speed_y)
        self.assertEqual(self.play_area.house.RECT.x, object_x + speed_x)
        self.assertEqual(
            self.play_area._hidden_objects['open_gate_left'].RECT.x,
            hidden_object_x + speed_x)

    def test_stop_player_movement(self):
        self.assertIs(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYUP, key=K_LEFT)), True)
        self.assertIsNone(self.play_area._scroll_speed)

    def test_tick(self):
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_LEFT))
        speed_x = self.play_area._scroll_speed[0]
        self.assertIs(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK)), True)
        self.assertGreater(self.play_area._scroll_speed[0], speed_x)

    def test_handle_player_collision(self):
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=KEYDOWN, key=K_UP))
        self._set_speed_for_collision()
        self.assertIsInstance(self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK)), str)

    def test_collide_with_closest_object(self):
        for obj in self.play_area._objects.values():
            obj.move((-800, 153))
        self.play_area._scroll_speed = (800, 0)
        collision = self.play_area.check_player_collision()
        assert collision  # for pytype
        self.assertIn('wall', collision.reason)

    def test_current_square(self):
        self.assertEqual(self.play_area.current_square, (0, 0))
        for obj in self.play_area._objects.values():
            obj.move((800, 0))
        self.assertEqual(self.play_area.current_square, (-1, 0))

    def test_visible_walls(self):
        self.play_area.draw()
        self.assertFalse(self.play_area.visible_walls)
        for obj in self.play_area._objects.values():
            obj.move((-400, 0))
        self.play_area.draw()
        wall, = self.play_area.visible_walls
        self.assertEqual(wall.SQUARE, (0, 0))
        self.assertEqual(wall.SIDE, walls.Side.RIGHT)

    def test_handle_click(self):
        self.assertIs(self.play_area.handle_click((288, 288)), True)

    def test_handle_key(self):
        for obj in self.play_area._objects.values():
            obj.move((950, -950))
        click_result = cast(interactions.Item, self.play_area.handle_click(
            self.play_area.key.RECT.center))
        self.assertEqual(click_result.name, 'key')

    def test_handle_outside_click(self):
        self.assertIs(self.play_area.handle_click((580, 288)), False)

    def test_use_key(self):
        for obj in self.play_area._objects.values():
            obj.move((-50, 450))
        use_result = cast(str, self.play_area.use_item('key'))
        self.assertIn('gate', use_result)
        self.assertNotIn('gate', self.play_area._objects)
        for gate_half in ('open_gate_left', 'open_gate_right'):
            self.assertIn(gate_half, self.play_area._objects)
            self.assertNotIn(gate_half, self.play_area._hidden_objects)

    def test_use_key_too_far(self):
        self.assertIsNone(self.play_area.use_item('key'))

    def test_can_collide(self):
        for name in itertools.chain(self.play_area._objects,
                                    self.play_area._hidden_objects):
            self.assertIsInstance(interactions.collide((0, 0), name),
                                  interactions.Collision)

    def test_can_obtain(self):
        for name in itertools.chain(self.play_area._objects,
                                    self.play_area._hidden_objects):
            self.assertIsInstance(interactions.obtain(name),
                                  (type(None), interactions.Item))

    def test_can_use(self):
        for name in itertools.chain(self.play_area._objects,
                                    self.play_area._hidden_objects):
            item = interactions.obtain(name)
            if item and item.success:
                self.assertIsInstance(interactions.use(name), interactions.Use)


if __name__ == '__main__':
    unittest.main()
