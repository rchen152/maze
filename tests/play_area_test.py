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

    def _move_player(self, x, y):
        for obj in itertools.chain(self.play_area._objects.values(),
                                   self.play_area._hidden_objects.values()):
            obj.move((-x, -y))

    def test_move(self):
        house_rect = self.play_area.house.RECT
        self.play_area.house.move((1, 1))
        self.assertEqual(self.play_area.house.RECT.topleft,
                         (house_rect.x + 1, house_rect.y + 1))

    def test_check_player_collision(self):
        self._set_speed_for_collision()
        self.assertTrue(self.play_area._check_player_collision())

    def test_check_player_nocollision(self):
        self.play_area._scroll_speed = (0, 0)
        self.assertFalse(self.play_area._check_player_collision())

    def test_wall(self):
        # This speed should collide the player with the wall below him.
        self.play_area._scroll_speed = (0, -400)
        self.assertTrue(self.play_area._check_player_collision())

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
        self._move_player(800, -153)
        self.play_area._scroll_speed = (800, 0)
        collision = self.play_area._check_player_collision()
        assert collision  # for pytype
        self.assertIn('wall', collision.reason)

    def test_current_square(self):
        self.assertEqual(self.play_area.current_square, (0, 0))
        self._move_player(-800, 0)
        self.assertEqual(self.play_area.current_square, (-1, 0))

    def test_visible_walls(self):
        self.play_area.draw()
        self.assertFalse(self.play_area.visible_walls)
        self._move_player(400, 0)
        self.play_area.draw()
        wall, = self.play_area.visible_walls
        self.assertEqual(wall.SQUARE, (0, 0))
        self.assertEqual(wall.SIDE, walls.Side.RIGHT)

    def test_handle_click(self):
        self.assertIs(self.play_area.handle_click((288, 288)), True)

    def test_handle_key(self):
        self._move_player(-950, 950)
        click_result = cast(interactions.Item, self.play_area.handle_click(
            self.play_area.key.RECT.center))
        self.assertIn('key', click_result.reason)

    def test_handle_outside_click(self):
        self.assertIs(self.play_area.handle_click((580, 288)), False)

    def test_use_key(self):
        self._move_player(50, -450)
        use_result = cast(interactions.Use, self.play_area.use_item('key'))
        self.assertIn('gate', use_result.reason)
        self.assertNotIn('gate', self.play_area._objects)
        for gate_half in ('open_gate_left', 'open_gate_right'):
            self.assertIn(gate_half, self.play_area._objects)
            self.assertNotIn(gate_half, self.play_area._hidden_objects)

    def test_use_key_too_far(self):
        self.assertIsNone(self.play_area.use_item('key'))

    def test_collide_flaming_shrubbery(self):
        self._move_player(3200, 1000)
        self.play_area.use_item('matches')
        self.play_area._scroll_speed = (0, -100)
        collision = self.play_area._check_player_collision()
        assert collision  # for pytype
        self.assertIn('flaming shrubbery', collision.reason)

    def test_remove_object(self):
        self.assertIn('key', self.play_area._objects)
        self.play_area.apply_effects(
            (interactions.Effect.remove_object('key'),))
        self.assertNotIn('key', self.play_area._objects)

    def test_add_object(self):
        self.assertNotIn('happy_cat', self.play_area._objects)
        self.play_area.apply_effects(
            (interactions.Effect.add_object('happy_cat'),))
        self.assertIn('happy_cat', self.play_area._objects)

    def test_can_collide(self):
        for name in itertools.chain(self.play_area._objects,
                                    self.play_area._hidden_objects):
            self.assertIsInstance(interactions.collide(name, (0, 0)),
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
            if not item:
                continue
            effects = list(item.item_effects)
            while effects:
                effect = effects.pop(0)
                if effect.type is not interactions.ItemEffectType.ADD:
                    continue
                for use in interactions.use(effect.target):
                    self.assertIsInstance(use, interactions.Use)
                    effects.extend(use.item_effects)

    def test_start_player_craving(self):
        self._move_player(2400, 800)
        self.play_area._scroll_speed = (-800, 0)
        self.assertIn('pre_crave', self.play_area._state)
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK))
        self.assertNotIn('pre_crave', self.play_area._state)

    def test_collide_invisible_wall_twice(self):
        self._move_player(2400, 800)
        self.play_area._scroll_speed = (-800, 0)
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK))
        self.play_area._scroll_speed = (-800, 0)
        self.play_area.handle_player_movement(
            test_utils.MockEvent(typ=play_area._TICK))

    def test_eat_fruit_no_craving(self):
        self.play_area._state = {'pre_crave': object()}
        use = cast(interactions.Use, self.play_area.use_item('peach'))
        self.assertIn('Yum', use.reason)
        self.assertIn('invisible_wall', self.play_area._objects)

    def test_eat_fruit_with_craving(self):
        self.play_area._state = {}
        use = cast(interactions.Use, self.play_area.use_item('peach'))
        self.assertIn('craving', use.reason)
        self.assertNotIn('invisible_wall', self.play_area._objects)

    def test_eat_fruit_after_craving(self):
        self.play_area._state = {}
        self.play_area.use_item('peach')
        use = cast(interactions.Use, self.play_area.use_item('peach'))
        self.assertIn('bloated', use.reason)

    def test_slot_block(self):
        self._move_player(1400, 2600)
        self.play_area.use_item('block_L')
        self.assertNotIn('puzzle_slot_L', self.play_area._objects)
        self.assertIn('slotted_block_L_in_L', self.play_area._objects)

    def test_slot_block_wrong(self):
        self._move_player(1400, 2600)
        self.play_area.use_item('block_E')
        self.assertNotIn('puzzle_slot_L', self.play_area._objects)
        self.assertIn('slotted_block_E_in_L', self.play_area._objects)

    def test_unslot_block(self):
        self._move_player(1400, 2600)
        self.play_area.use_item('block_E')
        item = cast(interactions.Item,
                    interactions.obtain('slotted_block_E_in_L'))
        self.play_area.apply_effects(item.play_area_effects)
        self.assertNotIn('slotted_block_E_in_L', self.play_area._objects)
        self.assertIn('puzzle_slot_L', self.play_area._objects)

    def test_solve_block_puzzle(self):
        self._move_player(1400, 2600)
        self.play_area.use_item('block_L')
        self.assertIn('puzzle_door', self.play_area._objects)
        self._move_player(120, 0)
        self.play_area.use_item('block_O')
        self.assertIn('puzzle_door', self.play_area._objects)
        self._move_player(200, 0)
        self.play_area.use_item('block_V')
        self.assertIn('puzzle_door', self.play_area._objects)
        self._move_player(140, 0)
        self.play_area.use_item('block_E')
        self.assertNotIn('puzzle_door', self.play_area._objects)


if __name__ == '__main__':
    unittest.main()
