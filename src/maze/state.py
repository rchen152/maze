"""Game state."""

import pygame

from common import color
from common import img
from common import state as common_state
from escape import room
from escape import state as escape_state
from . import play_area
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
                   "to find the exit.")

    def __init__(self, screen):
        self._play_area = play_area.Surface(screen)
        self._side_bar = side_bar.Surface(screen)
        self._side_bar.text_area.show(self._INTRO_TEXT)
        super().__init__(screen)
        pygame.time.set_timer(play_area.TICK, play_area.TICK_INTERVAL_MS)

    def draw(self):
        self._play_area.draw()
        self._side_bar.draw()
        pygame.display.update()

    def handle_player_movement(self, event):
        is_move_action = self._play_area.handle_player_movement(event)
        if is_move_action:
            self.draw()
        return is_move_action
