import pygame


class Grid:
    """ Class to draw a 5x5 alphamuddle grid
        surf: surface to be drawn on
        side: length of side
        cells: no of cells per side
        x, y: position of grid"""

    def __init__(self, surf, side, cells, x, y):
        self.surface = surf
        self.size = side
        self.cell = cells
        self.x = x
        self.y = y
        self.no = cells * cells
        self.cell_size = None
        self.grid_line = 4
        self.draw_grid = None  # surface for grid
        self.draw_cell = None  # list of surfaces for cells
        self.cell_pos = None  # list of cell positions

        self.font = pygame.font.SysFont('Tahoma', 24, False, False)

    def set_font(self, font):
        """ Set font for grid letters """
        self.font = pygame.font.SysFont('Tahoma', font, False, False)

    def set_line(self, line):
        """ Set thickness of grid lines """
        self.grid_line = line

    def draw(self):
        """ Draw an empty grid """
        size = (self.size, self.size)
        self.draw_grid = pygame.Surface(size)
        self.cell_size = c_width, c_height = ((self.size - self.grid_line * (self.cell + 1)) // self.cell,
                                              (self.size - self.grid_line * (self.cell + 1)) // self.cell)
        self.draw_grid.fill((0, 0, 0))
        self.draw_cell = []
        self.cell_pos = []
        for cell in range(self.no):
            self.draw_cell.append(pygame.Surface(self.cell_size))
        for cell in range(self.no):
            self.draw_cell[cell].fill((255, 255, 255))
            self.cell_pos.append(((self.grid_line + (self.grid_line + c_width) * (cell % self.cell),
                                   self.grid_line + (self.grid_line + c_width) * (cell // self.cell))))

        for cell in range(self.no):
            self.draw_grid.blit(self.draw_cell[cell], self.cell_pos[cell])
        self.surface.blit(self.draw_grid, (self.x, self.y))

    def draw_letters(self, string_lst):
        """ Draw letters in grid
            string_lst: list of letters '-' for empty"""
        string = ''.join(string_lst)
        no = 0
        for char in string:
            if char != "-":
                txt = self.font.render(char, True, (0, 0, 0))
                txt_rect = txt.get_rect(center=(self.cell_size[0] / 2, self.cell_size[1] / 2))
                self.draw_cell[no].blit(txt, txt_rect)
            else:
                self.draw_cell[no].fill((255, 255, 255))
            no += 1
        for cell in range(self.no):
            self.draw_grid.blit(self.draw_cell[cell], self.cell_pos[cell])
        self.surface.blit(self.draw_grid, (self.x, self.y))
