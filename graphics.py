import sys
import os
import os.path
import re

import pygame

import solver
import grid
import userinput
import textbox
from pygbuttons import Button
import constants as cons


# Define constants from file
BLACK = cons.BLACK
WHITE = cons.WHITE
D_LIGHT = cons.D_LIGHT
LIGHT_CYAN = cons.LIGHT_CYAN
CORNSILK = cons.CORNSILK
SCREEN_COL = CORNSILK

SCREEN_SIZE = cons.SCREEN_SIZE
LINE_START = cons.LINE_START
LINE_END = cons.LINE_END


class Screen:
    """ Class to define all user operations for game """

    def __init__(self, buttons):

        self.buttons = buttons
        pygame.init()

        self.grid_letters = None
        self.grid_final = None
        self.font = pygame.font.SysFont('Tahoma', 24, False, False)
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('AlphaMuddle')
        self.screen.fill(BLACK)
        self._show_text("Loading dictionary .....", 200, 305, WHITE, pygame.font.SysFont('Tahoma', 42, False, False))

        self.solve = solver.Solver()

        self._clear_screen()
        self.letters = ["SHAVE", "VALLI", "RALAT", "RALSA", "WRIST"]
        self.start_pattern = ["-A---", "--A--", "----A", "L----", "---R-"]
        self.button_complete1, self.button_complete2 = None, None

    def start_screen(self):
        """ Set up initial screen """
        self._clear_screen()
        self._set_buttons()

    def problem(self):
        """ Show problem on screen """
        self._clear_screen()

        letters_grid = grid.Grid(self.screen, 200, 5, 350, 50)
        letters_grid.draw()
        letters_grid.draw_letters(self.letters)

        start_grid = grid.Grid(self.screen, 200, 5, 650, 50)
        start_grid.draw()
        start_grid.draw_letters(self.start_pattern)
        pygame.display.flip()

    def get_answer(self):
        """ Solve problem and diplay answer """
        self._clear_space()
        self._show_text("Solutions", 200, 305)
        self.solve.set_problem(self.letters, self.start_pattern)
        solutions = self.solve.solve()
        if solutions:
            x, y = 350, 350
            for sol in solutions:
                solution_grid = grid.Grid(self.screen, 150, 5, x, y)
                solution_grid.set_font(16)
                solution_grid.set_line(2)
                solution_grid.draw()
                solution_grid.draw_letters([''.join(s) for s in sol])
                x += 205
                if x >= 900:
                    x, y = 350, y + 205
        else:
            self._show_text("No solutions found", 200, 405)

    def _show_text(self, txt, x, y, col=BLACK, font=None):
        """ Print text on screen """
        if font is None:
            font = self.font
        text = font.render(txt, True, col)
        self.screen.blit(text, (x, y))
        pygame.display.flip()

    def _set_buttons(self):
        """ Set up all buttons """
        button_new = Button(self.screen)
        button_new.set_button("New", x=50, y=50)
        self.buttons.add_button(button_new, "new")
        self.buttons.add_click(button_new, self.get_new)
        self.buttons.add_hover(button_new)
        self.buttons.set_active(button_new, True)
        self.buttons.set_visible(button_new, True)

        button_edit = Button(self.screen)
        button_edit.set_button("Edit", x=50, y=125)
        self.buttons.add_button(button_edit, "edit")
        self.buttons.add_click(button_edit, self.edit_grids)
        self.buttons.add_hover(button_edit)
        self.buttons.set_active(button_edit, True)
        self.buttons.set_visible(button_edit, True)

        button_show = Button(self.screen)
        button_show.set_button("Show", x=50, y=200)
        self.buttons.add_button(button_show, "show")
        self.buttons.add_click(button_show, self.problem)
        self.buttons.add_hover(button_show)
        self.buttons.set_active(button_show, True)
        self.buttons.set_visible(button_show, True)

        button_solve = Button(self.screen)
        button_solve.set_button("Solve", x=50, y=275)
        self.buttons.add_button(button_solve, "solve")
        self.buttons.add_click(button_solve, self.get_answer)
        self.buttons.add_hover(button_solve)
        self.buttons.set_active(button_solve, True)
        self.buttons.set_visible(button_solve, True)

        button_save = Button(self.screen)
        button_save.set_button("Save", x=50, y=350)
        self.buttons.add_button(button_save, "save")
        self.buttons.add_click(button_save, self.save_muddle)
        self.buttons.add_hover(button_save)
        self.buttons.set_active(button_save, True)
        self.buttons.set_visible(button_save, True)

        button_load = Button(self.screen)
        button_load.set_button("Load", x=50, y=425)
        self.buttons.add_button(button_load, "load")
        self.buttons.add_click(button_load, self.load_muddle)
        self.buttons.add_hover(button_load)
        self.buttons.set_active(button_load, True)
        self.buttons.set_visible(button_load, True)

        button_quit = Button(self.screen)
        button_quit.set_button("Quit", x=50, y=500)
        self.buttons.add_button(button_quit, "quit")
        self.buttons.add_click(button_quit, self.quit_muddle)
        self.buttons.add_hover(button_quit)
        self.buttons.set_active(button_quit, True)
        self.buttons.set_visible(button_quit, True)

        self.button_complete1 = Button(self.screen)
        self.button_complete1.set_button("Complete", x=350, y=575)
        self.buttons.add_button(self.button_complete1, "complete1")
        self.buttons.add_click(self.button_complete1, self._process_grid)
        self.buttons.add_hover(self.button_complete1)

        self.button_complete2 = Button(self.screen)
        self.button_complete2.set_button("Complete", x=650, y=575)
        self.buttons.add_button(self.button_complete2, "complete2")
        self.buttons.add_click(self.button_complete2, self._process_grid)
        self.buttons.add_hover(self.button_complete2)
        
    def _clear_screen(self):
        """ Clear screen area """
        self.screen.fill(SCREEN_COL)
        pygame.draw.line(self.screen, BLACK, LINE_START, LINE_END)

    def _clear_space(self):
        """ Clear solution area below line """
        space_rect = pygame.Rect(200, 305, 800, 450)
        pygame.draw.rect(self.screen, SCREEN_COL, space_rect, 0)
        pygame.display.flip()

    def _clear_problem(self):
        """ Clear problem area above line """
        space_rect = pygame.Rect(200, 50, 800, 250)
        pygame.draw.rect(self.screen, SCREEN_COL, space_rect, 0)
        pygame.display.flip()

    def get_new(self):
        """ Set up new problem grids """
        self._clear_space()
        self._clear_problem()
        self._show_text("Press Escape to abort", 200, 305)
        self._get_all()

    def edit_grids(self):
        """ Edit loaded problem grids """
        self._clear_space()
        self._show_text("Press Escape to abort", 200, 305)
        self._get_all(True)

    def _get_grid_letters(self, lets):
        """ Get dictionary self.grid_letters of all letters in grid by cell no {cell:letter} """
        self.grid_letters = dict.fromkeys(range(25), "")
        no = 0
        for row in lets:
            for col in range(5):
                self.grid_letters[no] = row[col]
                no += 1

    def _get_all(self, edit=False):
        """ Input letters into problem grids
            Edit grids if edit set to True
            else nput new grids """
        ok = True
        self.buttons.set_active(self.button_complete1, True)
        self.buttons.set_visible(self.button_complete1, True)

        if edit:
            self._get_grid_letters(self.letters)
        self._get_letters(350, 375, edit=edit)

        if self.grid_final[-1] == "/BREAK/":
            ok = False
        else:
            self.letters = [row[:] for row in self.grid_final]

            self.buttons.set_active(self.button_complete1, False)
            self.buttons.set_active(self.button_complete2, True)
            self.buttons.set_visible(self.button_complete2, True)

            if edit:
                self._get_grid_letters(self.start_pattern)

            self._get_letters(650, 375, "-", edit=edit)
            if self.grid_final[-1] == "/BREAK/":
                ok = False
            else:
                self.start_pattern = [row[:] for row in self.grid_final]

        self.buttons.set_active(self.button_complete2, False)
        self.buttons.set_visible(self.button_complete1, False)
        self.buttons.set_visible(self.button_complete2, False)

        if not ok:
            self._clear_space()
        else:
            self._show_text("Complete", 520, 600)

    def _get_letters(self, x, y, default="", edit=False):
        """ Input letters into grid
            default: shown in each cell before entry becomes default value for cell
            edit: True for edit mode"""
        input_rects = dict()
        inputs = dict()
        for row in range(5):
            for col in range(5):
                no = row * 5 + col
                input_rects[no] = pygame.Rect(x + col * 32, y + row * 32, 30, 30)
                inputs[no] = userinput.Uinput(self.screen, input_rects[no], self.font, 1, BLACK, frame=2)
                if edit:
                    inputs[no].show_input(self.grid_letters[no], col=inputs[no].background_colour)

        entry = True
        no = 0
        if not edit:
            self.grid_letters = dict.fromkeys(range(25), default)
        while entry:
            if edit:
                default = self.grid_letters[no]
            event, let = inputs[no].get_input(1, "u", default, cursor=False)
            if let == "/BREAK/":
                break
            if len(let) == 0:
                let = default
            self.grid_letters[no] = let

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed(3)[0]:
                    mouse = pygame.mouse.get_pos()
                    for (rhif, rect) in input_rects.items():
                        if rect.collidepoint(mouse):
                            no = rhif
                        elif self.buttons.check_pos(mouse) in ["complete1", "complete2"]:
                            entry = False

            elif event.type == pygame.KEYDOWN:
                inkey = event.key
                if inkey in [pygame.K_RETURN, pygame.K_RIGHT]:
                    no += 1
                elif inkey == pygame.K_LEFT and no > 0:
                    no -= 1
                elif inkey == pygame.K_UP and no > 4:
                    no -= 5
                elif inkey == pygame.K_DOWN and no < 20:
                    no += 5
            if no == 25:
                entry = False

        if not entry:
            self._process_grid()
        else:
            self.grid_final = ["/BREAK/"]

    def _process_grid(self):
        """ Convert grid letters dictionary to list of strings
            and set in self.grid_final """
        self.grid_final = []
        line = []
        for no in range(25):
            line.append(self.grid_letters[no] if self.grid_letters[no] else " ")
            if no % 5 == 4:
                self.grid_final.append(''.join(line))
                line = []

    def save_muddle(self):
        """ Save problem grids
            Next available number allocated as am## """
        self._clear_space()
        self._show_text("Press Escape to abort", 200, 305)
        # Get list of am##.txt files already present in directory muddles and get next availablet number
        scandir_iterator = os.scandir("muddles/")
        files = [os.path.splitext(item.name)[0] for item in scandir_iterator]
        next_no = max([int(name[2:]) for name in files if name[2:]])
        next_no += 1
        input_rect = pygame.Rect(250, 350, 200, 40)
        file_input = userinput.Uinput(self.screen, input_rect, self.font, 20, BLACK, frame=1)
        _, file_name = file_input.get_input(20, "n", "am" + str(next_no), keep_default=True)
        if file_name == "/BREAK/":
            self._clear_space()
            return
        _, f_extension = os.path.splitext(file_name)
        if file_name:
            file_name = "muddles/" + file_name
            if not f_extension:
                file_name = file_name + '.txt'
            if os.path.isfile(file_name):
                self._clear_space()
                self._show_text("File already exists", 250, 350)
            else:
                try:
                    with open(file_name, 'w') as f:
                        for row in range(5):
                            f.write(f"{self.letters[row]}\n")
                        for row in range(5):
                            f.write(f"{self.start_pattern[row]}\n")
                        self._clear_space()
                except (IOError, OSError):
                    self._clear_space()
                    self._show_text("Error while saving", 250, 450)

    def load_muddle(self):
        """ Load saved grids """
        self._clear_space()
        self._show_text("Press Escape to abort", 200, 305)
        # Get list of am##.txt files already present in directory muddles and sort by number
        scandir_iterator = os.scandir("muddles/")
        files = [os.path.splitext(item.name)[0] for item in scandir_iterator]
        files.sort(key=self._get_num)
        file_list = textbox.Textwrap(self.screen, pygame.Rect(250, 500, 500, 150),
                                     pygame.font.SysFont('Tahoma', 16, False, False),
                                     BLACK, D_LIGHT, 0, 1, BLACK)
        file_list.print_text(" ".join(files))
        input_rect = pygame.Rect(250, 425, 200, 40)
        file_input = userinput.Uinput(self.screen, input_rect, self.font, 20, BLACK, frame=1)
        _, file_name = file_input.get_input(20, "n")
        if file_name == "/BREAK/":
            self._clear_space()
            return
        _, f_extension = os.path.splitext(file_name)
        if file_name:
            file_name = "muddles/" + file_name
            if not f_extension:
                file_name = file_name + '.txt'
            self._clear_space()
            try:
                with open(file_name, 'r') as f:
                    complete_list = f.read().splitlines()
                    self.letters = []
                    for row in range(5):
                        self.letters.append(complete_list[row])
                    self.start_pattern = []
                    for row in range(5):
                        self.start_pattern.append(complete_list[row + 5])
                    self._clear_space()
                    self._clear_problem()
                    self.problem()
            except (IOError, OSError):
                self._clear_space()
                self._show_text("Cannot find that file", 250, 425)

    @staticmethod
    def _get_num(string):
        """ Find digits in string
            Return number if found
            Return 0 if not
        """
        match = re.search(r"\d+", string)
        if match:
            return int(match.group())
        return 0

    @staticmethod
    def quit_muddle():
        """ Quit application """
        pygame.quit()
        sys.exit()
