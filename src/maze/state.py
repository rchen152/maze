"""Game state."""

from common import color
from common import img
from escape import room
from escape import state as escape_state


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
