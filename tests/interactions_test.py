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
        self.assertEqual(effect.type, interactions.ItemEffectType.REMOVE)
        self.assertEqual(effect.target, 'key')

    def test_add_item(self):
        effect = interactions.Effect.add_item('key')
        self.assertEqual(effect.type, interactions.ItemEffectType.ADD)
        self.assertEqual(effect.target, 'key')

    def test_remove_object(self):
        effect = interactions.Effect.remove_object('key')
        self.assertEqual(effect.type, interactions.ObjectEffectType.REMOVE)
        self.assertEqual(effect.target, 'key')

    def test_add_object(self):
        effect = interactions.Effect.add_object('key')
        self.assertEqual(effect.type, interactions.ObjectEffectType.ADD)
        self.assertEqual(effect.target, 'key')


class CollideTest(unittest.TestCase):

    def test_wall(self):
        collision = interactions.collide((-3, 0), 'wall_1')
        self.assertIn('wall', collision.reason)


class ObtainTest(unittest.TestCase):

    def test_key(self):
        item = interactions.obtain('key')
        assert item  # for pytype
        self.assertCountEqual(item.item_effects,
                              (interactions.Effect.add_item('key'),))
        self.assertCountEqual(item.object_effects,
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
        self.assertCountEqual(use.item_effects, (
            interactions.Effect.remove_item('key'),))
        self.assertCountEqual(use.object_effects, (
            interactions.Effect.remove_object('gate'),
            interactions.Effect.add_object('open_gate_left'),
            interactions.Effect.add_object('open_gate_right')))


if __name__ == '__main__':
    unittest.main()
