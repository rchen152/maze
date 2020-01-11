"""Main entrypoint."""

import argparse
from escape import color
from escape import img
from escape import room
from escape import state
import pygame


def parse_args():
    parser = argparse.ArgumentParser(description='kitty maze game')
    parser.add_argument('-s', '--skip-title', action='store_true',
                        default=False, help='skip the title card')
    return parser.parse_args()


class ShortEscapeEnding(state.Ending):
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


def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode((1024, 576))
    pygame.display.set_caption('Kitty Maze')
    if not args.skip_title:
        state.TitleCard(screen).run()
    ShortEscapeEnding(screen).run()


if __name__ == '__main__':
    main()
