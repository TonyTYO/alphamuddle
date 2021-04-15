# -------------------------------------------------------------------------------
# Name:        textbox
# Purpose:     Allows text to be easily written to screen in pygame
# Author:      Tony
# Created:     25/08/2016
# Copyright:   (c) Tony 2016
# Licence:     Free to use
# -------------------------------------------------------------------------------

# ! /usr/bin/env python

""" Allows text to be easily written to screen in pygame
    Dependencies : pygame
"""
import sys
import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (169, 169, 169)


class TextRectException(Exception):
    """ Class that raises an exception if error found while printing string """

    def __init__(self, message=None, line="", extra_msg=""):
        super(TextRectException, self).__init__(message)
        self.message = message
        self.line = line
        self.extra_msg = extra_msg
        sys.tracebacklimit = 0

    def __str__(self):
        if self.line:
            self.message = self.message + " in text beginning '" + " ".join(self.line.split()[:5]) + "'."
        if self.extra_msg:
            self.message = self.message + "\n" + self.extra_msg
        return self.message


class Textwrap:
    """ Allows text to be written easily to screen in pygame

        Text can contain the following in-text commands
        /B to toggle bold text
        /I to toggle Italic
        /S to toggle underscore
        /C(colour tuple) to change colour /C to revert to original colour
        /F(sysfont name, size) to change font /F to revert to original font
    """
    __slots__ = ['base', 'flags', 'current', 'surface_dicts', 'surface_sizes', 'surface_dict', 'curr_line']

    def __init__(self, screen, rect, font, text_colour=(255, 255, 255),
                 background_colour=(0, 0, 0), justification=0, frame=0, frame_colour=(0, 0, 0)):
        """ Create the text box inside which text will be printed

            screen: surface to be blitted on - required
            rect:   rectangle to contain the writing - required
            font:   default font for text - required
            text_color: default colour for text
            background_color: colour of box background
            justification:  0(default)-left, 1-centred, 2-right.
                            add 10 for vertical centred
                            add 20 for vertical centred with room for dialogue buttons
            frame: 0(default)-no frame, otherwise thickness of frame
            frame_colour: Black(default) otherwise RGB colour triple

        """
        # Base values for instance stored in dictionary as follows
        # screen:display surface, font:font object, base_font:font specified in print_text()
        # rect:size of text area, text_colour:foreground colour,
        # background_colour:background colour (None - transparent)
        # justification:0-left,1-centred,2-right.
        # v_justifcation:vertical justification,
        # frame:0-no frame otherwise thickness of frame, frame_colour:Frame colour,

        self.base = {"screen": screen, "font": font, "base_font": font,
                     "rect": rect, "text_colour": text_colour,
                     "background_colour": background_colour,
                     "justification": justification, "v_justification": 0,
                     "frame": frame, "frame_colour": frame_colour}

        self.set_frame(frame, frame_colour)
        self.set_justification(justification)

        self.flags = {}  # flags used with inline formatting commands
        self.current = {}  # Internal attributes used by class instance while setting text
        self.surface_dicts = []  # list of dictionaries of surfaces, one for each line
        self.surface_sizes = []  # {surface no: (width, height)} for each line also -1:(total_width, max_height)
        self.surface_dict = {}  # Dictionary of surfaces making up each line
        self.curr_line = ""  # Line being processed

        self.set_defaults()

    # -----------------------------------------------------------------------------------------------------------
    # Set attributes

    def set_rect(self, *args):
        """ Set text rectangle
            args can be pygame.Rect, tuple or 4 numbers """
        if isinstance(args[0], pygame.Rect):
            self.base["rect"] = args[0]
        else:
            self.base["rect"] = pygame.Rect(*args)

    def set_font(self, font):
        """ Set font
            font has to be a pygame.font.Font or SysFont """
        self.base["base_font"] = font

    def set_text_colour(self, *args):
        """ Set default colour for text
            three RGB values or colour tuple """
        if isinstance(args[0], tuple):
            self.base["text_colour"] = args[0]
        else:
            self.base["text_colour"] = tuple(args)

    def set_back_colour(self, *args):
        """ Set colour of box background
            three RGB values or colour tuple """
        if isinstance(args[0], tuple):
            self.base["background_colour"] = args[0]
        else:
            self.base["background_colour"] = tuple(args)

    def set_justification(self, justification):
        """ Set justification
            0(default)-left, 1-centred, 2-right.
            add 10 for vertical centred
            add 20 for vertical centred with room for dialogue buttons """
        if justification >= 10:
            self.base["justification"] = justification % 10
            self.base["v_justification"] = justification // 10

    def set_frame(self, frame=0, frame_colour=(0, 0, 0)):
        """ Set frame type
            0(default)-no frame, otherwise thickness of frame
            frame_colour: Black(default) otherwise colour triple """
        self.base["frame"] = frame
        self.base["frame_colour"] = frame_colour

    # -----------------------------------------------------------------------------------------------------------

    def set_defaults(self):
        # flags used with inline formatting commands
        # bold:bold mode on flag, underline:underline mode on flag, italic:italic mode on flag
        # setcolour:colour change flag, setfont:font change flag

        self.flags = {"bold": False, "underline": False,
                      "italic": False, "setcolour": False, "setfont": False}

        # Internal attributes used by class instance while setting text
        # font and text_colour may be changed inline
        # line_length and surface_no used to build surfaces for the lines

        self.current = {"font": self.base["base_font"],
                        "text_colour": self.base["text_colour"],
                        "line_length": 0, "surface_no": 0}

        # Text is split into lengths as required to fit and each line rendered
        # If text attributes are changed these are rendered separately
        # All rendered surfaces for the line are stored in a dictionary {surface no: rendered surface}
        # All dictionaries are stored in a list
        self.surface_dicts = []  # list of dictionaries of surfaces, one for each line
        self.surface_sizes = []  # {surface no: (width, height)} for each line also -1:(total_width, max_height)
        self.surface_dict = {}  # Dictionary of surfaces making up each line

    # Process and render text
    # Split into lines of required width and render.
    def print_text(self, text, font=None):
        """ Print text inside box using defined parameters

            text: text to print(may include inline modifiers)
            font: optional, default used if not specified
        """
        if font is None:
            font = self.base["font"]
        self.base["base_font"] = font
        self.set_defaults()

        self._process_lines(text)
        surface = self._render_surfaces()
        self.base["screen"].blit(surface, self.base["rect"].topleft)
        return surface

    # self.surface_dicts holds all the dictionaries as a list
    # Processes all embedded codes and sends on parts with same attributes
    def _process_lines(self, text):
        """ Cut the text into lines to fit frame allowing for inline commands """

        self._reset_flags()
        self.surface_dicts = []
        process_dict = {'B': self._process_bold, 'C': self._process_colour,
                        'F': self._process_font, 'I': self._process_italic,
                        'S': self._process_underline}

        lines = text.splitlines()

        for line in lines:
            self.curr_line = line
            new_line = True

            while len(line) > 0:
                split_line = line.partition("\\")
                if len(split_line[0]) > 0:
                    self._render_line(split_line[0], self.current["font"], self.current["text_colour"], new_line)
                if split_line[1] == '\\':
                    line = process_dict.get(split_line[2][0], lambda args: None).__call__(split_line)
                    if line is None:
                        raise TextRectException("Unrecognized inline command '\\"
                                                + split_line[2][0] + "'", self.curr_line,
                                                r"Possible values are \B \C \F \I \S")
                else:
                    line = split_line[2]
                new_line = False
            self._line_surface()
        self._get_size()

    # Cut line to fit rectangle and render line or parts of line
    # The rendered parts for each line on screen are kept in a dictionary surface_dict
    # All dictionaries for the whole text are held in the list surface_dicts
    def _render_line(self, line, font, colour, state):
        """ Render all parts of each line """
        newline = state
        text_width = self.base["rect"].width - self.base["frame"] * 4  # max width for text
        if newline:
            self._start_line()
        self.do_line(line, font, colour, text_width)

    def do_line(self, line, font, colour, text_width):
        """ Fit line into current frame
            Start new lines if too long """
        if line == "":
            return
        if self.current["surface_no"] == 0:
            line = line.lstrip()
        excess = ""
        while self.current["line_length"] + font.size(line)[0] > text_width:
            pos = line.rfind(" ")
            if pos >= 0:
                excess = line[pos:] + excess
                line = line[:pos]
            elif font.size(line)[0] >= text_width:
                raise TextRectException("The word '" + line + "' is too long to fit specified rectangle",
                                        self.curr_line, "Needs at least "
                                        + str(font.size(line)[0] + self.base["frame"] * 4) + " for this font")
            else:
                line, excess = "", line + excess
        self.current["line_length"] += font.size(line)[0]
        self.surface_dict[self.current["surface_no"]] = font.render(line, True, colour)
        if excess:
            self._line_surface()
        else:
            self._continue_line()
        return self.do_line(excess, font, colour, text_width)

    def _start_line(self):
        """ Start a new line in rendered text """
        self.surface_dict = {}  # start dictionary at beginning of line
        self.current["surface_no"] = 0
        self.current["line_length"] = 0

    def _continue_line(self):
        """ Add surface to line dictionary """
        self.current["surface_no"] += 1

    def _line_surface(self):
        """ Append a complete line dictionary and start a new dictionary """
        self.surface_dicts.append(self.surface_dict)
        self.surface_dict = {}
        self.current["surface_no"] = 0
        self.current["line_length"] = 0

    def _get_size(self):
        """ Get width and height of each surface in each line
            Store as (width, height) in self.surface_sizes {surface no: (width, height)}
            Calculate total width and maximum height of text for each line and store as key value -1 """

        self.surface_sizes = []
        for dictionary in self.surface_dicts:
            size_dict = {}
            for key in dictionary:
                size_dict[key] = (dictionary[key].get_width(), dictionary[key].get_height())
            size_dict[-1] = (sum([val[0] for val in size_dict.values()]), max([val[1] for val in size_dict.values()]))
            self.surface_sizes.append(size_dict)

    # Blit lines of text from dictionaries onto surface
    def _render_surfaces(self):
        """ Render all lines onto surface """

        rect = self.base["rect"]
        totals = [size_dict.get(-1, (0, 0)) for size_dict in self.surface_sizes]
        total_height = sum([val[1] for val in totals])
        text_left = self.base["frame"] * 2  # left margin for text

        surface = pygame.Surface(rect.size)
        if self.base["background_colour"] is None:
            surface.fill(BLACK)
            surface.set_colorkey(BLACK)
        else:
            surface.fill(self.base["background_colour"])

        self._do_frame(surface)

        if self.base["v_justification"] > 0:
            text_y = (rect.height - (self.base["v_justification"] - 1) * 40 - total_height) / 2
        else:
            text_y = 0

        number = 0
        for dictionary in self.surface_dicts:
            size_dict = self.surface_sizes[number]
            text_width, text_height, text_start = 0, 0, 0

            for key in dictionary:
                if key == 0:
                    text_width, text_height = size_dict[-1]
                    if self.base["justification"] == 1:
                        text_start = (rect.width - text_width) / 2
                    elif self.base["justification"] == 2:
                        text_start = rect.width - text_width - text_left
                    else:
                        text_start = text_left
                # Blit sections aligned by base
                surface.blit(dictionary[key], (text_start, text_y + text_height - size_dict[key][1]))
                text_start += size_dict[key][0]
            text_y += text_height
            number += 1
        return surface

    def _do_frame(self, surface):
        """ Draw frame for text """

        rect = self.base["rect"]
        frame = self.base["frame"]

        if self.base["frame"] > 0:
            frame_rect = (0, 0, rect.width, rect.height)
            self._draw_frame(surface, self.base["frame_colour"], frame_rect, frame)

    @staticmethod
    def _draw_frame(surface, frame_colour, frame_rect, frame, i_colour=WHITE):
        """ Draw framed rectangle - avoids problems with corner pixels not drawing """
        i_frame = (frame_rect[0] + frame // 2, frame_rect[1] + frame // 2, frame_rect[2] - frame,
                   frame_rect[3] - frame)
        pygame.draw.rect(surface, frame_colour, frame_rect)
        pygame.draw.rect(surface, i_colour, i_frame)

    # Procedures to handle embedded commands
    def _process_bold(self, s_line):
        """ process inline \\B """

        if self.flags["bold"] is False:
            self.flags["bold"] = True
            self.current["font"].set_bold(True)
        else:
            self.flags["bold"] = False
            self.current["font"].set_bold(False)
        return s_line[2][1:]

    def _process_underline(self, s_line):
        """ process inline \\S """

        if self.flags["underline"] is False:
            self.flags["underline"] = True
            self.current["font"].set_underline(True)
        else:
            self.flags["underline"] = False
            self.current["font"].set_underline(False)
        return s_line[2][1:]

    def _process_italic(self, s_line):
        """ process inline \\I """

        if self.flags["italic"] is False:
            self.flags["italic"] = True
            self.current["font"].set_italic(True)
        else:
            self.flags["italic"] = False
            self.current["font"].set_italic(False)
        return s_line[2][1:]

    def _process_colour(self, s_line):
        """ process inline \\C """

        if self.flags["setcolour"] is False:
            line = s_line[2]
            col_string = line[2:].split(")", 1)[0].split(",")
            self.current["text_colour"] = tuple(int(x) for x in col_string)
            self.flags["setcolour"] = True
            line = s_line[2][2:].split(")", 1)[1]
        else:
            self.current["text_colour"] = self.base["text_colour"]
            self.flags["setcolour"] = False
            line = s_line[2][1:]
        return line

    def _process_font(self, s_line):
        """ process inline \\F """

        if self.flags["setfont"] is False:
            line = s_line[2]
            font_string = line[2:].split(")", 1)[0].split(",")
            font_tuple = tuple(x for x in font_string)
            self.current["font"] = pygame.font.SysFont(font_tuple[0], int(font_tuple[1]))
            self.flags["setfont"] = True
            line = s_line[2][2:].split(")", 1)[1]
        else:
            self.current["font"] = self.base["base_font"]
            self.flags["setfont"] = False
            line = s_line[2][1:]
        return line

    # reset all flags to False
    def _reset_flags(self):
        """ Reset all flags to False """

        self.flags["bold"] = False
        self.flags["underline"] = False
        self.flags["italic"] = False
        self.flags["setcolour"] = False
        self.flags["setfont"] = False
