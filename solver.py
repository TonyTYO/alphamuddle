from pygaddag import GADDAG


class Solver:
    """ Class to solve an alphamuddle.
        set_problem to send letters and patterns
        solve returns list of solution grids
    """

    def __init__(self):

        self.graph = GADDAG()
        self.graph.safeload("english/pygaddag.p")

        self.letters = None  # list of letters in full square
        self.occurrences = None  # dictionary of letter frequencies letter: no
        self.start_grid = None  # original grid to solve (list of lists)
        self.init_grid = None  # initial grid ie start grid with all reflected letters entered
        self.singles = None  # list of all single occurrence letters
        self.even = None  # list of all even occurrence letters
        self.odd = None  # list of all odd occurrence letters
        self.solutions = None  # list of grids of solutions found

    def set_problem(self, letters, patterns):
        """ Initial processing of problem
            Remove any letters already used in start grid
            from available letters """

        self.letters = [let.lower() for string in letters for let in string]
        self.letters.sort()
        self.start_grid = [list(p.lower()) for p in patterns]

        self.occurrences = dict()
        for let in self.letters:
            self.occurrences[let] = self.occurrences.get(let, 0) + 1
        self.singles, self.even, self.odd = [], [], []
        for let, no in self.occurrences.items():
            if no == 1:
                self.singles.append(let)
                self.odd.append(let)
            elif no % 2 != 0:
                self.odd.append(let)
            else:
                self.even.append(let)

        used_letters = [let for patt in self.start_grid for let in patt if let.isalpha()]
        for let in used_letters:
            if let in self.letters:
                self.letters.remove(let)

    def solve(self):
        """ Solve grid """
        self.solutions = []
        self.try_grid()
        return self.solutions

    def try_grid(self):
        """ Check for missing reflected letters and start recursive search for solutions """
        self.init_grid, self.letters = self.check_diagonal(self.start_grid, self.letters)
        if not self.letters:
            self.solutions = ["ERROR"]
            return
        solution = [row[:] for row in self.init_grid]
        self.traverse(0, self.letters, solution)

    def traverse(self, row, letters, solution):
        """ Recursive search for solution """
        if row > 4 and self.check_muddle(solution):
            self.solutions.append([row[:] for row in solution])
            return solution
        else:
            for rw in range(5):
                for col in range(5):
                    if rw >= row and col >= row:
                        solution[rw][col] = self.init_grid[rw][col]
        pattern = self.get_pattern(row, solution)
        possibles = list(self.graph.find_lett_patt(letters[:], pattern))
        possibles = [word for word in possibles if self.check_singles(row, word)]
        possibles = [word for word in possibles if self.check_pattern(row, word, letters, pattern)]
        for word in possibles:
            if row == 0:
                solution = [row[:] for row in self.init_grid]
            self.set_word(word, row, solution)
            new_letters = self.get_letters(word, letters, row, pattern)
            self.traverse(row + 1, new_letters, solution)

    @staticmethod
    def check_diagonal(grid, letters):
        """ Insert any missing reflected letters and remove from list
            of available letters """
        grid = grid[:]
        try:
            for row in range(5):
                for col in range(5):
                    if grid[row][col].isalpha() and grid[col][row] == "-":
                        grid[col][row] = grid[row][col]
                        letters.remove(grid[col][row])
                    elif grid[col][row].isalpha() and grid[row][col] == "-":
                        grid[row][col] = grid[col][row]
                        letters.remove(grid[row][col])
        except ValueError:
            letters.clear()
        return grid, letters

    def check_singles(self, row, word):
        """ Check for single occurrence letters set off diagonal
            Return False if found """
        for pos in range(len(word)):
            if word[pos] in self.singles and pos != row:
                return False
        return True

    @staticmethod
    def get_letters(word, letters, row, pattern):
        """ Return new list of letters
            having removed all letters used in word
            Note: used once if at row otherwise used twice (row and column)"""
        new_letters = letters[:]
        for i in range(5):
            if word[i] != pattern[i]:
                new_letters.remove(word[i])
                if i != row:
                    new_letters.remove(word[i])
        return new_letters

    @staticmethod
    def check_pattern(row, word, letters, pattern):
        """ Check word doesn't use too many instances of any letter """
        word = word[:]
        for i in range(5):
            if word[i] == pattern[i]:
                word[i] = "-"  # Remove letters already in grid ie in pattern
        word.extend(word)  # each word used twice (row and column)
        word.remove(word[row])  # letter at row only used once
        for i in range(5):
            if word[i].isalpha() and word.count(word[i]) > letters.count(word[i]):
                return False
        return True

    @staticmethod
    def get_pattern(row, solution):
        """ Return pattern as string """
        return ''.join(solution[row])

    @staticmethod
    def set_word(word, row, solution):
        """ Set word in grid as row and column """
        for i in range(5):
            solution[row][i] = word[i]
            solution[i][row] = word[i]

    def check_muddle(self, muddle):
        """ Check if solution complete and correct """
        if any("-" in sublist for sublist in muddle):
            return False
        t_muddle = self.transpose(muddle)
        if (len(muddle) == len(t_muddle)) and (all(row in t_muddle for row in muddle)):
            return True
        else:
            return False

    @staticmethod
    def transpose(lst):
        """ Transpose rows and columns """
        return [list(i) for i in zip(*lst)]

    @staticmethod
    def get_newlist(char, lst, flag=False):
        """ Remove used char from list and return
            if flag is False return unaltered list """
        if not flag or not lst:
            new_list = lst
        else:
            new_list = list(lst)
            if char in new_list:
                new_list.remove(char)
        return new_list

    @staticmethod
    def print_list(lst):
        if not isinstance(lst, list):
            print(None)
        else:
            for row in lst:
                print(row)
