"""Tests for maze.collisions."""

import unittest
from maze import interactions


class CloserThanTest(unittest.TestCase):

    def test_closer_than(self):
        collision = interactions.Collision((-3, 0), '')
        self.assertTrue(collision.closer_than((-4, 0)))

    def test_not_closer_than(self):
        collision = interactions.Collision((-3, 0), '')
        self.assertFalse(collision.closer_than((-2, 0)))


class EffectTest(unittest.TestCase):

    def test_remove_item(self):
        effect = interactions.Effect.remove_item('key')
        self.assertIs(effect.type, interactions.ItemEffectType.REMOVE)
        self.assertEqual(effect.target, 'key')

    def test_add_item(self):
        effect = interactions.Effect.add_item('key')
        self.assertIs(effect.type, interactions.ItemEffectType.ADD)
        self.assertEqual(effect.target, 'key')

    def test_remove_object(self):
        effect = interactions.Effect.remove_object('key')
        self.assertIs(effect.type, interactions.ObjectEffectType.REMOVE)
        self.assertEqual(effect.target, 'key')

    def test_add_object(self):
        effect = interactions.Effect.add_object('key')
        self.assertIs(effect.type, interactions.ObjectEffectType.ADD)
        self.assertEqual(effect.target, 'key')

    def test_hide_object(self):
        effect = interactions.Effect.hide_object('key')
        self.assertIs(effect.type, interactions.ObjectEffectType.HIDE)
        self.assertEqual(effect.target, 'key')


class CollideTest(unittest.TestCase):

    def test_wall(self):
        collision = interactions.collide((-3, 0), 'wall_1')
        self.assertIn('wall', collision.reason)


class ObtainTest(unittest.TestCase):

    def test_key(self):
        item = interactions.obtain('key')
        assert item  # for pytype
        self.assertSequenceEqual(item.item_effects,
                                 (interactions.Effect.add_item('key'),))
        self.assertSequenceEqual(item.object_effects,
                                 (interactions.Effect.remove_object('key'),))
        self.assertIn('key', item.reason)

    def test_noop(self):
        self.assertIsNone(interactions.obtain('wall_1'))


class UseTest(unittest.TestCase):

    def test_name(self):
        use, = interactions.use('key')
        self.assertEqual(use.activator, 'gate')

    def test_reason(self):
        use, = interactions.use('key')
        self.assertIn('gate', use.reason)

    def test_effects(self):
        use, = interactions.use('key')
        self.assertSequenceEqual(use.item_effects,
                                 (interactions.Effect.remove_item('key'),))
        self.assertSequenceEqual(use.object_effects, (
            interactions.Effect.remove_object('gate'),
            interactions.Effect.add_object('open_gate_left'),
            interactions.Effect.add_object('open_gate_right')))


class ConfigTest(unittest.TestCase):

    def test_squares(self):
        squares = interactions.config('invisible_wall', 'squares')
        self.assertIs(squares, interactions.Squares.ALL)

    def test_squares_default(self):
        squares = interactions.config('doesnotexist', 'squares')
        self.assertIs(squares, interactions.Squares.DEFAULT)

    def test_inflation(self):
        inflation = interactions.config('puzzle_slot_L', 'inflation')
        self.assertEqual(inflation, (-40, 100))

    def test_inflation_default(self):
        inflation = interactions.config('doesnotexist', 'inflation')
        self.assertEqual(inflation, interactions._DEFAULT_INFLATION)


if __name__ == '__main__':
    unittest.main()
