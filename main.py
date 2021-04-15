# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pygaddag import GADDAG, Node

class ScrabbleWordsText:
    """ Class to check words in English Scrabble """

    # Initialise values
    def __init__(self, filename, player=None):
        self.player = player  # identify player
        wordfile = None
        try:
            wordfile = open(filename, 'r')  # list of allowed scrabble words
        except IOError as e:
            print(e)
            self.words = []
        wordsread = wordfile.readlines()  # read into list
        self.words = [i.strip() for i in wordsread]  # remove white space
        self.choice = []  # list of possible words from rack

    def check_word(self, word):
        """ Check if word is in scrabble list
            Return True or False
            Return None if check not operational """

        if not self.words:
            return None
        word = ''.join(word)
        return next((True for w in self.words if w == word), False)



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


    graph = GADDAG()
    print(graph)
    graph.load("english/pygaddag.p")
    print(list(graph.ask(graph.contains_lett, "art", "derp")))
    print(list(graph.contains_lett_patt(["a", "r", "t"], ["d", "e", "r", "p"], {0: "e", 1: "r"})))
    ans = list(graph.contains_lett_patt(["a"], ["d", "e", "r", "p"], {0: "r"}))
    print(ans)
    print([w[1] for w in ans if len(w[1]) == 6])
    ans = list(graph.find_lett_patt(["d", "e", "r", "p"], "-ar---"))
    print(ans)
    ans = list(graph.find_lett_patt(["g", "r", "e", "e", "r", "a", "h", "t", "e", "a", "l", "t", "r", "c"], "-h---"))
    print(len(ans), ans)
    for w in ans:
        print(''.join(w), graph.is_in(w))
        # print(''.join(w), graph.is_in(w), list(graph.contains(w)))

    # checker = ScrabbleWordsText("english/sowpods.txt")
    # for w in checker.words:
    #     if graph.check_pattern(w, "-h---"):
    #         if all(l in ["g", "r", "e", "e", "r", "a", "h", "t", "e", "a", "l", "t", "r", "c"] for l in w):
    #             print(w)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
