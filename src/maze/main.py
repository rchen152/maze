"""Main entrypoint."""

import argparse
from common import state as common_state
import pygame
from . import state


def parse_args():
    parser = argparse.ArgumentParser(description='kitty maze game')
    parser.add_argument('-s', '--skip-title', action='store_true',
                        default=False, help='skip the title card')
    return parser.parse_args()


def main():
    args = parse_args()
    pygame.init()
    screen = pygame.display.set_mode(common_state.RECT.size)
    pygame.display.set_caption('Kitty Maze')
    if not args.skip_title:
        common_state.TitleCard(screen).run()
        state.ShortEscapeEnding(screen).run()
    state.Game(screen).run()


if __name__ == '__main__':
    main()
