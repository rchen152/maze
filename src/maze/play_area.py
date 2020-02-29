"""Gameplay area."""

import itertools
import pygame
from pygame.locals import *
from typing import Optional, Sequence, Union

from common import color
from common import img
from common import state
from . import interactions
from . import objects
from . import play_map
from . import play_objects
from . import walls

_TICK = pygame.USEREVENT
_TICK_INTERVAL_MS = 100
_PLAYER_SPEED_INTERVAL = 5
# We scroll the background instead of moving the player.
_PLAYER_MOVES = {
    K_LEFT: (_PLAYER_SPEED_INTERVAL, 0), K_RIGHT: (-_PLAYER_SPEED_INTERVAL, 0),
    K_UP: (0, _PLAYER_SPEED_INTERVAL), K_DOWN: (0, -_PLAYER_SPEED_INTERVAL)}
_PLAYER_FEET_HEIGHT = 15


def _shift_speed(speed, direction):
    return tuple(s + direction * _PLAYER_SPEED_INTERVAL * s / abs(s) if s else s
                 for s in speed)


def _decelerate(speed) -> Optional[interactions.Speed]:
    speed = _shift_speed(speed, -1)
    return None if speed == (0, 0) else speed


def _accelerate(speed):
    return _shift_speed(speed, 1)


class Surface(objects.Surface):
    """A subsurface with movable objects on it."""

    RECT = pygame.Rect(0, 0, state.RECT.h, state.RECT.h)
    # We don't include the player here because he is a special fixed object.
    OBJECTS = play_objects.VISIBLE
    _HIDDEN_OBJECTS: objects.ObjectsType = play_objects.HIDDEN
    _STATE: Sequence[str] = play_objects.STATE

    def __init__(self, screen):
        super().__init__(screen)
        self._hidden_objects = {name: cls(self._surface)
                                for name, cls in self._HIDDEN_OBJECTS.items()}
        self._state = {name: object() for name in self._STATE}
        self.player = img.load('player', self._surface,
                               (state.RECT.h / 2, state.RECT.h / 2),
                               (-0.5, -0.5))
        self._scroll_speed: Optional[interactions.Speed] = None
        self._player_feet_rect = pygame.Rect(
            self.player.RECT.x, self.player.RECT.bottom - _PLAYER_FEET_HEIGHT,
            self.player.RECT.w, _PLAYER_FEET_HEIGHT)

    def _effective_rect(self, rect):
        return rect.move(
            tuple(play_map.HOUSE_POS[i] - self.house.RECT.topleft[i]
                  for i in range(2)))

    def _square(self, rect):
        return play_map.pos_to_square(self._effective_rect(rect).midbottom)

    @property
    def current_square(self):
        return self._square(self._player_feet_rect)

    @property
    def visible_walls(self):
        return {wall for name, wall in self._objects.items()
                if walls.match(name) and self._visible(wall) and
                self.current_square in wall.adjacent_squares}

    def draw(self):
        self._surface.fill(color.BLUE)
        super().draw()
        self.player.draw()

    def _check_player_collision(self) -> Optional[interactions.Collision]:
        # Check if the player's feet would hit anything if he took a step
        # against the background scroll direction.

        def _get_player_path_rect(speed):
            next_feet_rect = self._player_feet_rect.move(
                tuple(-s for s in speed))
            return self._player_feet_rect.union(next_feet_rect)

        player_path_rect = _get_player_path_rect(self._scroll_speed)
        closest_collision: Optional[interactions.Collision] = None
        for name, obj in self._objects.items():
            if obj.RECT.colliderect(player_path_rect):
                # Find the maximum speed at which the player won't collide.
                speed: Optional[interactions.Speed] = _decelerate(
                    self._scroll_speed)
                while speed:
                    if not obj.RECT.colliderect(_get_player_path_rect(speed)):
                        break
                    speed = _decelerate(speed)
                if closest_collision and closest_collision.closer_than(speed):
                    continue
                closest_collision = interactions.collide(name, speed)
        return closest_collision

    def handle_player_movement(self, event) -> Union[bool, str]:
        if event.type == KEYUP and event.key in _PLAYER_MOVES:
            self._scroll_speed = None
            pygame.time.set_timer(_TICK, 0)
            return True
        elif event.type == KEYDOWN and event.key in _PLAYER_MOVES:
            self._scroll_speed = _PLAYER_MOVES[event.key]
            pygame.time.set_timer(_TICK, _TICK_INTERVAL_MS)
        elif event.type == _TICK:
            if not self._scroll_speed:
                # The player has been stopped by an obstacle.
                return True
            self._scroll_speed = _accelerate(self._scroll_speed)
        else:
            return False
        collision: Optional[interactions.Collision] = (
            self._check_player_collision())
        if collision:
            # Move the player as close to the obstacle as possible.
            speed = collision.max_nocollision_speed
            move_result = collision.reason
            self._scroll_speed = None
            self.apply_effects(collision.play_area_effects)
        else:
            speed = self._scroll_speed
            move_result = True
        if speed:
            for obj in itertools.chain(self._objects.values(),
                                       self._hidden_objects.values()):
                obj.move(speed)
        return move_result

    def _player_close_to(self, name):
        rect = self._objects[name].RECT
        close_enough_squares: interactions.SquaresType = interactions.config(
            name, 'squares')
        if close_enough_squares is interactions.Squares.ALL:
            return True
        if close_enough_squares is interactions.Squares.DEFAULT:
            close_enough_squares = {self._square(rect)}
        if self.current_square not in close_enough_squares:
            return False
        inflation = interactions.config(name, 'inflation')
        return rect.inflate(*inflation).colliderect(self.player.RECT)

    def apply_effects(self, effects):
        for effect in effects:
            target = effect.target
            if effect.type is interactions.ObjectEffectType.REMOVE:
                del self._objects[target]
            elif effect.type is interactions.ObjectEffectType.ADD:
                self._objects[target] = self._hidden_objects[target]
                del self._hidden_objects[target]
            elif effect.type is interactions.ObjectEffectType.HIDE:
                self._hidden_objects[target] = self._objects[target]
                del self._objects[target]
            else:
                assert effect.type is interactions.StateEffectType.REMOVE
                if target in self._state:
                    del self._state[target]

    def handle_click(self, pos) -> Union[bool, interactions.Item]:
        if not self.collidepoint(pos):
            return False
        for name, obj in self._objects.items():
            if obj.collidepoint(pos) and self._player_close_to(name):
                item: Optional[interactions.Item] = interactions.obtain(name)
                if item:
                    break
        else:
            return True
        # Note that we can't apply the effects of picking up the item yet: we
        # have to first check whether we have space for it.
        return item or True

    def _activate_item(self, activator):
        for one_activator in activator:
            if (one_activator not in self._state and (
                    one_activator not in self._objects or
                    not self._player_close_to(one_activator))):
                return False
        return True

    def use_item(self, name) -> Optional[interactions.Use]:
        uses: Sequence[interactions.Use] = interactions.use(name)
        for use in uses:
            if not self._activate_item(use.activator):
                continue
            self.apply_effects(use.play_area_effects)
            return use
        return None
