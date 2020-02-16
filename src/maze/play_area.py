"""Gameplay area."""

import itertools
import pygame
from pygame.locals import *
from typing import Optional, Union

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


def _decelerate(speed):
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

    def __init__(self, screen):
        super().__init__(screen)
        self._hidden_objects = {name: cls(self._surface)
                                for name, cls in self._HIDDEN_OBJECTS.items()}
        self.player = img.load('player', self._surface,
                               (state.RECT.h / 2, state.RECT.h / 2),
                               (-0.5, -0.5))
        self._scroll_speed = None
        self._player_feet_rect = pygame.Rect(
            self.player.RECT.x, self.player.RECT.bottom - _PLAYER_FEET_HEIGHT,
            self.player.RECT.w, _PLAYER_FEET_HEIGHT)

    def _square(self, rect):
        return play_map.pos_to_square(
            rect.move(tuple(play_map.HOUSE_POS[i] - self.house.RECT.topleft[i]
                            for i in range(2))).midbottom)

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

    def check_player_collision(self) -> Optional[interactions.Collision]:
        # Check if the player's feet would hit anything if he took a step
        # against the background scroll direction.

        def _get_player_path_rect(speed):
            next_feet_rect = self._player_feet_rect.move(
                tuple(-s for s in speed))
            return self._player_feet_rect.union(next_feet_rect)

        player_path_rect = _get_player_path_rect(self._scroll_speed)
        closest_collision = None
        for name, obj in self._objects.items():
            if obj.RECT.colliderect(player_path_rect):
                # Find the maximum speed at which the player won't collide.
                speed = _decelerate(self._scroll_speed)
                while speed:
                    if not obj.RECT.colliderect(_get_player_path_rect(speed)):
                        break
                    speed = _decelerate(speed)
                if closest_collision and closest_collision.closer_than(speed):
                    continue
                closest_collision = interactions.collide(speed, name)
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
        collision = self.check_player_collision()
        if collision:
            # Move the player as close to the obstacle as possible.
            speed = collision.max_nocollision_speed
            move_result = collision.reason
            self._scroll_speed = None
        else:
            speed = self._scroll_speed
            move_result = True
        if speed:
            for obj in itertools.chain(self._objects.values(),
                                       self._hidden_objects.values()):
                obj.move(speed)
        return move_result

    def _player_close_to(self, rect):
        if self.current_square != self._square(rect):
            return False
        return rect.inflate(100, 100).colliderect(self.player.RECT)

    def handle_click(self, pos) -> Union[bool, interactions.Item]:
        if not self.collidepoint(pos):
            return False
        for name, obj in self._objects.items():
            if obj.collidepoint(pos) and self._player_close_to(obj.RECT):
                item = interactions.obtain(name)
                break
        else:
            return True
        if not item:
            return True
        if item.consumed:
            del self._objects[item.name]
        return item

    def use_item(self, name) -> Optional[str]:
        uses = interactions.use(name)
        for use in uses:
            if use.activator not in self._objects or not self._player_close_to(
                    self._objects[use.activator].RECT):
                continue
            for effect in use.effects:
                target = effect.target
                if effect.type is interactions.UseEffectType.REMOVE_OBJECT:
                    del self._objects[target]
                else:
                    assert effect.type is interactions.UseEffectType.ADD_OBJECT
                    self._objects[target] = self._hidden_objects[target]
                    del self._hidden_objects[target]
            return use.reason
        return None
