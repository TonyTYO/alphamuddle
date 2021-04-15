import sys

import pygame
from pygame.locals import *
import graphics
import pygbuttons

FPS = 60


def main():
    """ Main game loop
        Uses pygbuttons.Buttons to process all buttons
    """

    buttons = pygbuttons.Buttons()
    screen = graphics.Screen(buttons)
    screen.start_screen()

    clock = pygame.time.Clock()
    running = True

    while running:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                running = False
        elif event.type == QUIT:
            running = False

        buttons.process_buttons(event)

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    main()
    pygame.quit()
    sys.exit()
