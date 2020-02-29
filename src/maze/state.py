"""Game state."""

import itertools
import pygame
from pygame.locals import *
from typing import Optional, Union

from common import color
from common import img
from common import state as common_state
from escape import room
from escape import state as escape_state
from . import interactions
from . import play_area
from . import play_map
from . import play_objects
from . import side_bar


class ShortEscapeEnding(escape_state.Ending):
    """The ending to kitty-escape without the congratulations card."""

    def __init__(self, screen):
        keypad = img.load(screen, factory=room.KeyPad)
        keypad.text = '9710'  # opens the keypad so 'OK' will be centered
        keypad.text = 'OK'
        super().__init__(screen, color.GREY, keypad)

    def handle_tick(self, event):
        ret = super().handle_tick(event)
        if not ret:
            return False
        if self._frame == 3:
            self.active = False
        return True


class Game(common_state.GameState):

    _INTRO_TEXT = ("You've escaped the house, but you're lost in a maze. Try "
                   "to find an exit.")
    _OBTAIN_FAIL_TEXT = 'Your arms are too full to pick anything up.'
    _USE_FAIL_TEXT = "You can't do anything with the {} right now."
    _END_TEXT = ("Roses are red, I've a confession to make. There is no exit, "
                 "it's a closed heart shape. You've reached the end, Happy "
                 "Valentine's Day!")

    def __init__(self, screen, debug, cheat):
        self._play_area = play_area.Surface(screen)
        self._side_bar = side_bar.Surface(screen)
        self._side_bar.text_area.show(self._INTRO_TEXT)
        self._debug = debug
        if debug:
            self._interact_objects = self._debug_compute_interact_objects()
        else:
            self._interact_objects = None
        if cheat:
            x, y = cheat
            for obj in itertools.chain(
                    self._play_area._objects.values(),
                    self._play_area._hidden_objects.values()):
                obj.move((-x * 800, -y * 800))
        super().__init__(screen)

    def _debug_compute_interact_objects(self):
        interact_objects = set()
        for name in itertools.chain(self._play_area._objects,
                                    self._play_area._hidden_objects):
            item = interactions.obtain(name)
            if not item:
                continue
            interact_objects.add(name)
            effects = list(item.item_effects)
            while effects:
                effect = effects.pop(0)
                if effect.type is not interactions.ItemEffectType.ADD:
                    continue
                for use in interactions.use(effect.target):
                    if use.activator:
                        interact_objects.update(use.activator)
                    effects.extend(use.item_effects)
        return interact_objects

    def _debug_draw(self):
        rects = [(self._play_area._player_feet_rect, color.BRIGHT_GREEN)]
        for name, obj in self._play_area._objects.items():
            rects.append((obj.RECT, color.BRIGHT_GREEN))
            if (name not in self._interact_objects or interactions.config(
                    name, 'squares') is interactions.Squares.ALL):
                continue
            inflation = interactions.config(name, 'inflation')
            rects.append((obj.RECT.inflate(*inflation), color.LIGHT_CREAM))
        for rect, rect_color in rects:
            if isinstance(rect, play_objects._MultiRect):
                rects_to_draw = rect._get_rects()
            else:
                rects_to_draw = [rect]
            for rect in rects_to_draw:
                pygame.draw.rect(self._play_area._surface, rect_color, rect, 2)

    def draw(self):
        self._play_area.draw()
        self._side_bar.draw()
        if self._debug:
            self._debug_draw()
        pygame.display.update()

    def handle_player_movement(self, event):
        move_result: Union[bool, str] = self._play_area.handle_player_movement(
            event)
        if not move_result:
            return move_result
        if isinstance(move_result, str):
            self._side_bar.text_area.show(move_result)
        elif event.type == KEYDOWN:
            self._side_bar.text_area.show(None)
        self._side_bar.mini_map.update(
            self._play_area.current_square, self._play_area.visible_walls)
        if self._play_area.current_square == play_map.END_SQUARE:
            self._side_bar.mini_map.turn_red()
            self._side_bar.text_area.show(self._END_TEXT)
        self.draw()
        return True

    def _apply_item_effects(self, effects, pos=None):
        for effect in effects:
            if effect.type is interactions.ItemEffectType.REMOVE:
                self._side_bar.consume_item(effect.target, pos)
            else:
                assert effect.type is interactions.ItemEffectType.ADD
                self._side_bar.add_item(effect.target)

    def handle_click(self, event):
        if event.type != MOUSEBUTTONDOWN or event.button != 1 or (
                not self._play_area.collidepoint(event.pos) and
                not self._side_bar.collidepoint(event.pos)):
            return False
        click_result: Union[bool, interactions.Item] = (
            self._play_area.handle_click(event.pos))
        if click_result:
            if isinstance(click_result, interactions.Item):
                if self._side_bar.has_space_for(click_result.item_effects):
                    self._play_area.apply_effects(
                        click_result.play_area_effects)
                    self._apply_item_effects(click_result.item_effects)
                    self._side_bar.text_area.show(click_result.reason)
                else:
                    self._side_bar.text_area.show(self._OBTAIN_FAIL_TEXT)
        else:
            click_result: Union[bool, str] = self._side_bar.handle_click(
                event.pos)
            assert click_result
            if isinstance(click_result, str):
                use_result: Optional[interactions.Use] = (
                    self._play_area.use_item(click_result))
                if use_result:
                    self._apply_item_effects(use_result.item_effects, event.pos)
                    self._side_bar.text_area.show(use_result.reason)
                else:
                    self._side_bar.text_area.show(
                        self._USE_FAIL_TEXT.format(
                            click_result.replace('_', ' ')))
        self.draw()
        return True

    def handle_debug_location_request(self, event):
        if not self._debug or event.type != KEYDOWN or event.key != K_l:
            return False
        effective_player_feet_pos = self._play_area._effective_rect(
            self._play_area._player_feet_rect).midbottom
        square = []
        offsets = []
        for i in range(2):
            shift = effective_player_feet_pos[i] - play_map.START_POS[i]
            square.append(shift // play_map.SQUARE_LENGTH)
            offsets.append(shift % play_map.SQUARE_LENGTH)
        print(tuple(square), tuple(offsets))
        return True
