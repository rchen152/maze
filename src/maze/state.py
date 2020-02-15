"""Game state."""

import itertools
import pygame
from pygame.locals import *

from common import color
from common import img
from common import state as common_state
from escape import room
from escape import state as escape_state
from . import interactions
from . import play_area
from . import play_map
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
    _USE_FAIL_TEXT = "You can't do anything with the {} right now."
    _END_TEXT = ("Roses are red, I've a confession to make. There is no exit, "
                 "it's a closed heart shape. You've reached the end, Happy "
                 "Valentine's Day!")

    def __init__(self, screen, cheat):
        self._play_area = play_area.Surface(screen)
        self._side_bar = side_bar.Surface(screen)
        self._side_bar.text_area.show(self._INTRO_TEXT)
        if cheat:
            x, y = cheat
            for obj in itertools.chain(
                    self._play_area._objects.values(),
                    self._play_area._hidden_objects.values()):
                obj.move((-x * 800, -y * 800))
        super().__init__(screen)

    def draw(self):
        self._play_area.draw()
        self._side_bar.draw()
        pygame.display.update()

    def handle_player_movement(self, event):
        move_result = self._play_area.handle_player_movement(event)
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

    def handle_click(self, event):
        if event.type != MOUSEBUTTONDOWN or event.button != 1 or (
                not self._play_area.collidepoint(event.pos) and
                not self._side_bar.collidepoint(event.pos)):
            return False
        click_result = self._play_area.handle_click(event.pos)
        if click_result:
            if isinstance(click_result, interactions.Item):
                if click_result.success:
                    self._side_bar.add_item(click_result.name)
                self._side_bar.text_area.show(click_result.reason)
        else:
            click_result = self._side_bar.handle_click(event.pos)
            assert click_result
            if isinstance(click_result, str):
                use_result = self._play_area.use_item(click_result)
                if use_result:
                    self._side_bar.consume_item(click_result)
                    self._side_bar.text_area.show(use_result)
                else:
                    self._side_bar.text_area.show(
                        self._USE_FAIL_TEXT.format(
                            click_result.replace('_', ' ')))
        self.draw()
        return True
