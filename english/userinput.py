# -------------------------------------------------------------------------------
# Name:        userinput
# Purpose:     Get user input in pygame
# Author:      Tony
# Created:     16/03/2021
# Copyright:   (c) Tony 2021
# Licence:     Free to use
# -------------------------------------------------------------------------------

# ! /usr/bin/env python

""" Allows easy userinput in pygame
    Dependencies : pygame
"""
from time import time

import pygame

# Define the colors we will use in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT = (170, 170, 170)
DARK = (100, 100, 100)


class Uinput:
    """ Create user input box allowing text input

        screen: surface on which input blitted
        rect: bounding rectangle for input
        font: default font for text
        max_length: maximum characters in input (input rect will be based on this)
        text_color: default colour for text
        background_color: colour of box background when not got focus
        active_color: colour of box background when active
        frame:  0 (default)-no frame, integer: thickness of frame
        frame_colour: Black(default) otherwise colour triple
    """

    def __init__(self, screen, rect, font, max_length, text_colour=BLACK, background_colour=LIGHT,
                 active_colour=WHITE, frame=0, frame_colour=BLACK):

        self.screen = screen  # Display screen
        self.rect = rect  # Bounding rectangle for input
        self.font = font  # Font for input
        self.max_length = max_length  # Maximum length of input
        self.text_colour = text_colour  # Colour for text
        self.background_colour = background_colour  # Background colour for input box when created
        self.active_colour = active_colour  # Background colour when active (gets focus)
        self.frame = frame  # Thickness of frame around rectangle - 0 for no frame
        self.frame_colour = frame_colour  # Colour of frame

        self.input_surface = pygame.Surface((self.rect.width - self.frame * 2, self.rect.height - self.frame * 2))
        self.input_surface.fill(self.background_colour)
        self.screen.blit(self.input_surface, (self.rect.x + self.frame, self.rect.y + self.frame))
        pygame.draw.rect(self.screen, self.frame_colour, self.rect, self.frame)
        pygame.display.update()
        self.input_x = self.rect.x + self.frame * 2
        self.input_y = self.rect.y

        self.format_input = {"n": self.no_format, "u": self.upper_case,
                             "l": self.lower_case, "p": self.proper_case}
        self.length = None

    def get_input(self, length=None, form="n", default=None, cursor=True, keep_default=False):
        """ Get and show user input
            End input with Return or mouse click outside input rectangle
            Escape returns "/BREAK/" as input string
            Returns the event and input string

            length: length of input if different from max_length
            form: n/u/l/p - as entered/upper case/lower case/proper case
            default: default value for input
            cursor: if False input cursor not shown
            keep_default: If False default wiped when key pressed
        """
        if length is None:
            self.length = self.max_length
        else:
            self.length = length

        self.input_surface.fill(self.active_colour)
        self.screen.blit(self.input_surface, (self.rect.x + self.frame, self.rect.y + self.frame))
        pygame.display.update()
        pygame.key.set_repeat(0, 50)

        if default:
            input_string = default
            current_string = list(default)
            self.show_input(input_string)
        else:
            input_string = ""
            current_string = []
        first = True

        last_time = time()
        if not cursor:
            show_cursor = False
        else:
            show_cursor = True
            cursor = True
        while True:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN:
                inkey = event.key
                if first and not keep_default:
                    input_string = ""
                    current_string = []
                    first = False
                    self.show_input(input_string)
                if inkey == pygame.K_ESCAPE:
                    return event, "/BREAK/"
                if inkey == pygame.K_BACKSPACE:
                    current_string = current_string[0:-1]
                elif inkey in [pygame.K_RETURN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN]:
                    input_string = "".join(current_string)
                    self.show_input(input_string)
                    break
                elif inkey <= 127 and len(current_string) < length:
                    current_string.append(event.unicode)
                    current_string = self.format_input[form](current_string)
                input_string = "".join(current_string)
                self.show_input(input_string)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if not self.rect.collidepoint(mouse):
                    input_string = "".join(current_string)
                    self.show_input(input_string)
                    break

            if show_cursor:
                if time() - last_time > 0.2:
                    if cursor:
                        self.show_input(input_string)
                        cursor = False
                    else:
                        self.show_input(input_string + "_")
                        cursor = True
                    last_time = time()

        return event, input_string

    def show_input(self, input_string, col=None, just=None):
        """ Render and display input text """
        if col is None:
            col = self.active_colour
        self.input_surface.fill(col)
        text = self.font.render(input_string, True, self.text_colour)
        if just:
            text_rect = text.get_rect(center=(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2))
        else:
            text_rect = text.get_rect(topleft=(self.rect.x + 4, self.rect.y))
        self.screen.blit(self.input_surface, (self.rect.x + self.frame, self.rect.y + self.frame))
        self.screen.blit(text, text_rect)
        pygame.display.flip()

    @staticmethod
    def no_format(string):
        """ Show input as entered """
        return string

    @staticmethod
    def upper_case(string):
        """ Change all input to upper case """
        if string:
            string[-1] = string[-1].upper()
        return string

    @staticmethod
    def lower_case(string):
        """ Change all input to lower case """
        if string:
            string[-1] = string[-1].lower()
        return string

    @staticmethod
    def proper_case(string):
        """ Change all input to proper case """
        if string:
            if len(string) == 1 or string[-2] == " ":
                string[-1] = string[-1].upper()
            else:
                string[-1] = string[-1].lower()
        return string
