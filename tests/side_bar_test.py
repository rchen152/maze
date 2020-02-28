"""Tests for maze.side_bar."""

import pygame
import unittest

from common import color
from common import test_utils
from maze import interactions
from maze import side_bar
from maze import walls


class MiniMapTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.mini_map = side_bar.MiniMap(self.screen)

    def test_update_squares(self):
        self.mini_map.update((0, 0), set())
        self.mini_map.update((1, 1), set())
        self.assertCountEqual(self.mini_map._explored_squares, {(0, 0), (1, 1)})

    def test_update_same_square(self):
        self.mini_map.update((0, 0), set())
        self.mini_map.update((0, 0), set())
        self.assertEqual(self.mini_map._explored_squares, {(0, 0)})

    def test_update_seen_walls(self):
        self.assertFalse(self.mini_map._seen_walls)
        self.mini_map.update((0, 0), {walls.ALL['wall_sright'](self.screen)})
        wall, = self.mini_map._seen_walls
        self.assertEqual(wall.SQUARE, (0, 0))
        self.assertEqual(wall.SIDE, walls.Side.RIGHT)

    def test_draw(self):
        self.mini_map.draw()

    def test_turn_red(self):
        self.assertNotEqual(self.mini_map._square_color, color.RED)
        self.mini_map.turn_red()
        self.assertEqual(self.mini_map._square_color, color.RED)


class TextAreaTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.text_area = side_bar.TextArea(self.screen)
        self.max_width = side_bar.TextArea.RECT.w - side_bar.TextArea._LEFT_PAD

    def test_one_line(self):
        self.text_area.show('This is some text.')
        block, = self.text_area._text
        self.assertEqual(block.value, 'This is some text.')

    def test_multiple_lines(self):
        pygame.font.SysFont.return_value.size = (
            lambda text: (self.max_width * len(text.split()), 10))
        self.text_area.show('Two lines.')
        block1, block2 = self.text_area._text
        self.assertEqual(block1.size, (self.max_width, 10))
        self.assertEqual(block1.value, 'Two')
        self.assertEqual(block2.size, (self.max_width, 10))
        self.assertEqual(block2.pos, (block1.pos[0], block1.pos[1] + 10))
        self.assertEqual(block2.value, 'lines.')

    def test_whitespace(self):
        pygame.font.SysFont.return_value.size = (
            lambda text: (self.max_width * len(text.split()) // 2, 10))
        self.text_area.show('Two words per line.')
        block1, block2 = self.text_area._text
        self.assertEqual(block1.value, 'Two words')
        self.assertEqual(block2.value, 'per line.')

    def test_show_none(self):
        self.text_area.show(None)
        self.assertFalse(self.text_area._text)


class SurfaceTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.side_bar = side_bar.Surface(self.screen)

    def test_add_item(self):
        self.assertIsNone(self.side_bar.item_cell0.item)
        self.side_bar.add_item('key')
        self.assertIsNotNone(self.side_bar.item_cell0.item)

    def test_handle_outside_click(self):
        self.assertIs(self.side_bar.handle_click((288, 288)), False)

    def test_handle_noop_click(self):
        self.assertIs(self.side_bar.handle_click(
            self.side_bar.text_area.RECT.move(576, 0).center), True)

    def test_handle_empty_cell_click(self):
        self.assertIs(self.side_bar.handle_click(
            self.side_bar.item_cell0.RECT.move(576, 0).center), True)

    def test_handle_item_cell_click(self):
        self.side_bar.add_item('key')
        self.assertEqual(self.side_bar.handle_click(
            self.side_bar.item_cell0.RECT.move(576, 0).center), 'key')

    def test_consume_item(self):
        self.side_bar.add_item('key')
        self.assertIsNotNone(self.side_bar.item_cell0.item)
        self.side_bar.consume_item('key', None)
        self.assertIsNone(self.side_bar.item_cell0.item)

    def test_item_multiples_no_pos(self):
        self.side_bar.add_item('peach')
        self.side_bar.add_item('peach')
        self.side_bar.consume_item('peach', None)
        self.assertIsNone(self.side_bar.item_cell0.item)
        self.assertIsNotNone(self.side_bar.item_cell1.item)

    def test_item_multiples_with_pos(self):
        self.side_bar.add_item('peach')
        self.side_bar.add_item('peach')
        self.side_bar.consume_item(
            'peach', self.side_bar.item_cell1.RECT.move(576, 0).center)
        self.assertIsNotNone(self.side_bar.item_cell0.item)
        self.assertIsNone(self.side_bar.item_cell1.item)

    def test_has_space_for_remove_item(self):
        self.assertTrue(self.side_bar.has_space_for(
            (interactions.Effect.remove_item('key'),)))

    def test_has_space_for_add_item(self):
        self.assertTrue(
            self.side_bar.has_space_for((interactions.Effect.add_item('key'),)))

    def test_no_space_for_add_item(self):
        for _ in range(8):
            self.side_bar.add_item('peach')
        self.assertFalse(
            self.side_bar.has_space_for((interactions.Effect.add_item('key'),)))

    def test_has_space_for_remove_then_add_item(self):
        for _ in range(8):
            self.side_bar.add_item('peach')
        self.assertTrue(self.side_bar.has_space_for(
            (interactions.Effect.remove_item('peach'),
             interactions.Effect.add_item('key'))))

    def test_no_space_for_add_then_remove_item(self):
        for _ in range(8):
            self.side_bar.add_item('peach')
        self.assertFalse(self.side_bar.has_space_for(
            (interactions.Effect.add_item('key'),
             interactions.Effect.remove_item('peach'))))

    def test_no_space_after_noop_remove_item(self):
        item_effects = (interactions.Effect.remove_item('peach'),) + (
            interactions.Effect.add_item('peach'),) * 9
        self.assertFalse(self.side_bar.has_space_for(item_effects))


if __name__ == '__main__':
    unittest.main()
