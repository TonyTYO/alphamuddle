# -------------------------------------------------------------------------------
# Name:        pygbuttons
# Purpose:     Buttons for pygame
# Author:      Tony
# Created:     16/03/2021
# Copyright:   (c) Tony 2021
# Licence:     Free to use
# -------------------------------------------------------------------------------

# ! /usr/bin/env python

""" Allows setup and use of buttons in pygame
    Dependencies : pygame
"""

import pygame
from pygame.locals import *

# Define the colours used in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT = (170, 170, 170)
DARK = (100, 100, 100)
D_LIGHT = (220, 220, 220)
D_DARK = (192, 192, 192)
MAGENTA = (255, 0, 255)


class Buttons:
    """ Class to manage and process buttons.
        buttons = pygbuttons.Buttons()
        define all individual buttons using Button class
        and insert following into event processing loop to handle all button operations
        buttons.process_buttons(event)
    """

    __slots__ = ['_buttons', '_b_rects', '_active', '_on_hover', '_on_click', '_is_down', '_visible', '_process']

    def __init__(self):
        self._buttons = dict()  # Button: name
        self._b_rects = dict()  # Button: button rect
        self._active = dict()  # Button: flag if button is active (True/False)
        self._on_hover = dict()  # Button: function to execute when mouse over button or None
        self._on_click = dict()  # Button: function to execute when button clicked or None
        self._is_down = dict()  # Button: flag if button is down (True/False)
        self._visible = dict()  # Button: flag if button is visible (True/False)
        self._process = True  # flag set False if dictionaries being altered, processing is halted

    def add_button(self, button, name):
        """ Add a button """
        self._process = False
        self._buttons[button] = name
        self._b_rects[button] = button.surface_rect
        self._is_down[button] = False
        self._active[button] = False
        self._visible[button] = False
        self.add_click(button)
        self.add_hover(button)
        self._process = True

    def remove_button(self, button):
        """ Remove button """
        self._process = False
        self._buttons.pop(button, None)
        self._b_rects.pop(button, None)
        self._is_down.pop(button, None)
        self._active.pop(button, None)
        self._visible.pop(button, None)
        self._process = True

    def add_click(self, button, func=None):
        """ Function to be applied when button is clicked """
        self._process = False
        self._on_click[button] = func
        self._process = True

    def add_hover(self, button, func=None):
        """ Function to be applied when mouse hovers over button """
        self._process = False
        self._on_hover[button] = func
        self._process = True

    def set_active(self, button, active):
        """ Set button status as active or inactive
            When inactive mouse is ignored
            active: boolean True/False """
        self._process = False
        self._active[button] = active
        if not active:
            button.inactive()
        else:
            button.active()
        self._process = True

    def set_visible(self, button, visible):
        """ Set button to be visible
            visible: boolean True/False """
        self._process = False
        self._visible[button] = visible
        if visible:
            button.draw()
        else:
            self._active[button] = False
            button.blank()
        self._process = True

    def check_pos(self, pos):
        """ Return button located at pos
            None if no button found """
        if self._buttons:
            for (but, rect) in self._b_rects.items():
                if self._active[but]:
                    if rect.collidepoint(pos):
                        return self._buttons[but]
        return None

    def _button_down(self, mouse):
        """ if mouse above an active button
            set is_down flag and activate button's on_click procedure """
        if self._buttons:
            for (but, rect) in self._b_rects.items():
                if self._active[but]:
                    if rect.collidepoint(mouse):
                        but.on_click()
                        self._is_down[but] = True

    def _button_up(self, mouse):
        """ if mouse above an active button
            Activate button click procedures """
        if self._buttons:
            for (but, rect) in self._b_rects.items():
                if self._active[but]:
                    if rect.collidepoint(mouse):
                        but.draw()
                        self._is_down[but] = False
                        if self._on_click[but]:
                            self._on_click[but]()

    def _button_hover(self, mouse):
        """ if mouse above an active button
            Activate button hover procedures """
        if self._buttons:
            for (but, rect) in self._b_rects.items():
                if self._active[but] and not self._is_down[but]:
                    if rect.collidepoint(mouse):
                        but.on_hover()
                        if self._on_hover[but]:
                            self._on_hover[but]()
                    else:
                        but.draw()

    def process_buttons(self, event):
        """ Check if mouse interacting with button
            and react accordingly """
        if self._process:
            mouse = pygame.mouse.get_pos()
            if event.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(3)[0]:
                    self._button_down(mouse)
            elif event.type == MOUSEBUTTONUP:
                if not pygame.mouse.get_pressed(3)[0]:
                    self._button_up(mouse)
            else:
                self._button_hover(mouse)


class Button(object):
    """ Class defining buttons on screen

        screen: surface on which button is displayed
        transcolour: transparent colour for background
    """

    __slots__ = ['screen', 'trans_colour', 'font', 'x', 'y', 'w', 'h',
                 'col', 'h_col', 'd_col', 't_col', 'in_text', 'in_button',
                 'label', 'text', 'button_rect', 'text_rect', 'surface_rect',
                 'surface', 'background']

    def __init__(self, screen, transcolour=MAGENTA):

        self.screen = screen  # Display screen
        self.trans_colour = transcolour  # Transparent colour for background
        self.font = pygame.font.SysFont('Tahoma', 24, False, False)  # Default font for button text
        self.x, self.y = 0, 0  # Position of button
        self.w, self.h = 140, 40  # Width and height of button
        self.col = DARK  # Colour of button
        self.h_col = LIGHT  # Colour when mouse passing over
        self.d_col = BLACK  # Colour when clicked
        self.t_col = WHITE  # Colour of text on button
        self.in_text = D_LIGHT  # Text colour on inactive button
        self.in_button = D_DARK  # Button colour for inactive button

        self.label = None  # Actual text for button
        self.text = None  # Rendered text for button
        self.button_rect = None
        self.text_rect = None
        self.surface_rect = None
        self.surface = None
        self.background = None

    def set_button(self, txt, font=None, x=None, y=None, w=None, h=None,
                   col=None, h_col=None, d_col=None, t_col=None, in_text=None, in_button=None):
        """ Set up button details - defaults for all apart from the text
            Does not draw button

            txt: text for button
            font: font for button text
            x, y: position of button
            w, h: width and height of button
            col: colour of button
            h_col: colour when mouse hovering over button
            d_col: colour when button down on button
            t_col: colour of text on button
            in_text: text colour on inactive button
            in_button: button colour for inactive button
        """

        self.label = txt
        if font:
            self.font = font
        if x:
            self.x = x
        if y:
            self.y = y
        if w:
            self.w = w
        if h:
            self.h = h
        if col:
            self.col = col
        if h_col:
            self.h_col = h_col
        if d_col:
            self.d_col = d_col
        if t_col:
            self.t_col = t_col
        if in_text:
            self.in_text = in_text
        if in_button:
            self.in_button = in_button

        self.surface_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.button_rect = pygame.Rect(0, 0, self.w, self.h)
        self.text = self.font.render(txt, True, self.t_col)
        _, text_height = self.font.size(txt)
        self.text_rect = self.text.get_rect(center=(self.button_rect.width / 2,
                                                    self.button_rect.height / 2))
        self.background = pygame.Surface(self.surface_rect.size)
        bg = self.screen.subsurface(self.surface_rect)
        self.background.blit(bg, (0, 0))
        self.surface = pygame.Surface(self.button_rect.size)
        self.surface.set_colorkey(self.trans_colour)
        self.surface.fill(self.trans_colour)
        self._build(self.col)

    def draw(self, col=None):
        """ Draw button on screen """
        self._build(col)
        self.screen.blit(self.surface, self.surface_rect)
        pygame.display.update(self.surface_rect)

    def _build(self, col=None):
        """ Build button on a surface """
        if col is None:
            col = self.col
        self.surface.set_colorkey(self.trans_colour)
        self.surface.fill(self.trans_colour)
        pygame.draw.rect(self.surface, col, self.button_rect, 0, 5)
        self.surface.blit(self.text, self.text_rect)

    def on_hover(self):
        """ Run to change colour when mouse hovering over button """
        self.draw(self.h_col)

    def on_click(self):
        """ Run to change colour when mouse clicked on button """
        self.draw(self.d_col)

    def inactive(self):
        """ Change to inactive colours for button """
        self.text = self.font.render(self.label, True, self.in_text)
        _, text_height = self.font.size(self.label)
        self.text_rect = self.text.get_rect(center=(self.button_rect.width / 2,
                                                    self.button_rect.height / 2))
        self.surface = pygame.Surface(self.button_rect.size)
        self._build(self.in_button)
        self.screen.blit(self.surface, self.surface_rect)
        pygame.display.update(self.surface_rect)

    def active(self):
        """ Change to active colours for button """
        self.text = self.font.render(self.label, True, self.t_col)
        _, text_height = self.font.size(self.label)
        self.text_rect = self.text.get_rect(center=(self.button_rect.width / 2,
                                                    self.button_rect.height / 2))
        self.surface = pygame.Surface(self.button_rect.size)
        self._build(self.col)
        self.screen.blit(self.surface, self.surface_rect)
        pygame.display.update(self.surface_rect)

    def blank(self):
        """ Remove from display """
        self.screen.blit(self.background, self.surface_rect)
        pygame.display.update(self.surface_rect)
