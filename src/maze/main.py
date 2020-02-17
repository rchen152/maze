"""Main entrypoint."""

import argparse
import os
import pygame

from common import state as common_state
from . import state


_IS_SOURCE_INSTALL = __file__.endswith(
    os.path.sep + os.path.join('src', 'maze', 'main.py'))


def _parse_cheat(cheat):
    return tuple(float(i.replace('~', '-')) for i in cheat.split(','))


def parse_args():
    parser = argparse.ArgumentParser(description='kitty maze game')
    parser.add_argument('-s', '--skip-title', action='store_true',
                        default=False, help='skip the title card')
    if _IS_SOURCE_INSTALL:
        parser.add_argument('--debug', action='store_true')
        parser.add_argument('--cheat', action='store', default=None,
                            type=_parse_cheat)
    return parser.parse_args()


def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode(common_state.RECT.size)
    pygame.display.set_caption('Kitty Maze')
    if not args.skip_title:
        common_state.TitleCard(screen).run()
        state.ShortEscapeEnding(screen).run()
    debug = getattr(args, 'debug', False)
    cheat = getattr(args, 'cheat', None)
    state.Game(screen, debug, cheat).run()


if __name__ == '__main__':
    main()
