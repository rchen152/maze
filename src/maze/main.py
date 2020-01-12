"""Main entrypoint."""

import argparse
from escape import state as escape_state
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
    screen = pygame.display.set_mode((1024, 576))
    pygame.display.set_caption('Kitty Maze')
    if not args.skip_title:
        escape_state.TitleCard(screen).run()
    state.ShortEscapeEnding(screen).run()


if __name__ == '__main__':
    main()
