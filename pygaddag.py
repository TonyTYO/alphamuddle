""" Module containing class to define a GADDAG data structure

    Class GADDAG contains all functions for creating and searching
    the GADDAG

    Class Node used internally by class GADDAG

    from pygaddag import GADDAG, Node
    must be in the main package module for the pickle load to work

"""
import io
import time
import pickle
import gzip

# Following line required if openload is used with Qt
# from PyQt5.QtWidgets import QApplication

WORDLIST_PATH = 'sowpods\\sowpods.txt'

# Following line required if openload is used with Qt
# APP = QApplication([]).instance()


class GADDAG:
    """A data structure that allows extremely fast searching of words."""

    def __init__(self, words=None):
        self._len = 0
        self._changed = False
        self._root = Node()

        if words is not None:
            self.add(words)

    def __len__(self):
        if self._changed:
            self._len = 0
            for _ in self:
                self._len += 1

        return self._len

    def __contains__(self, word):
        return self._has(word.lower())

    def __iter__(self):
        return self._crawl_end(self.root, [])

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented

        if len(self) != len(other):
            return False

        return self.root == other.root

    @property
    def root(self):
        """Returns the root node of the GADDAG."""
        return self._root

    @staticmethod
    def ask(fnct, *args):
        """
        Returns result of applying function to strings
        Allows specification of inputs as strings rather than lists

        Args:
            fnct: name of function
            *args: parameters of function as strings
        """
        return fnct(*list(map(list, args)))

    # ------------------------------------------------------------------------------
    # Creation routines

    def create_from_file(self, filename=WORDLIST_PATH):
        """
        Create a GADDAG from a text file of a lexicon. If no filename is supplied
        then it will default to the WORDLIST_PATH setting. The text file should
        only have the words in the lexicon, one per line, with a blank line
        at the very end.

        Args:
            filename: An existing file-like object to read from.
        """

        wordcount = 0
        with open(filename, 'r') as f:
            for word in f.readlines():
                stripped = word.rstrip()
                if len(stripped) > 1:
                    self.add(stripped)  # Chop the newline
                    wordcount += 1
                    if (wordcount % 100) == 0:
                        print("{0}\r".format(wordcount), end="")

    def save(self, filename):
        """
        Save the GADDAG to a file.

        Args:
            filename: A path or an existing file-like object to write to.
        """
        with gzip.open(filename, "wb") as f:
            f.write(pickle.dumps(self._root, 4))

    def load(self, filename):
        """
        Load a GADDAG from file.

        Args:
            filename: A path or an existing file-like object to read from.
        """
        with gzip.open(filename, "rb") as f:
            self._root = pickle.loads(f.read())
        self._changed = True

    def openload(self, filename):
        """
        Load a GADDAG from file with event processing in Qt.
        The commented out import and APP specification need to be restored

        Args:
            filename: A path or an existing file-like object to read from.
        """
        with gzip.open(OpenStream(filename, "rb")) as f:
            self._root = pickle.loads(f.read())
        self._changed = True

    def safeload(self, filename):
        """
        Load a GADDAG from file.
        Allows pickle to work without importing classes in main module

        Args:
            filename: A path or an existing file-like object to read from.
        """
        with gzip.open(OpenStream(filename, "rb")) as f:
            self._root = SafeUnpickler(f).load()
        self._changed = True
        print("DEBUG end unpickling")
        print()

    def add(self, content):
        """
        Add a word (or words) to the GADDAG.

        Args:
            content: A single word (str) or iterable of words.
        """
        # if isinstance(content, str):
        #    return self._add_word(content)

        # for word in content:
        #    self._add_word(word)
        return self._add_word(content)

    def _add_word(self, word):
        """
        Add a word to the GADDAG.

        Args:
            word: A word to be added to the GADDAG.

        Returns:
            `True` if the word was added to the GADDAG, `False` if it already existed.
        """
        # word = word.lower()

        if ''.join(word) in self:
            return False

        # Create path from word[-1]
        node = self.root.add_path(word[-1::-1])
        node.add_end("+")

        # Create path from word[-2]
        node = self.root.add_path(word[-2::-1])
        node = node.add_edge("+")
        node.add_end(word[-1])

        # Create remaining paths (partially minimised)
        for m in range(len(word) - 3, -1, -1):
            existing_node = node

            node = self.root.add_path(word[m::-1])
            node = node.add_edge("+")

            char = word[m + 1]
            if char in node:
                # Current node already has an edge for this char,
                # try to point the edge at the existing_node instead
                if node[char] and node[char].edges != existing_node.edges:
                    raise AttributeError("Nodes do not have to same edges.")

                node.set_edge(char, existing_node)
            else:
                node.add_edge(char, existing_node)

        # Set changed flag so len is recalculated
        self._changed = True
        return True

    # ------------------------------------------------------------------------------
    # General interrogation routines

    def is_in(self, word):
        """
        Check that a given word is in the GADDAG.

        Args:
            word: The word to be checked for.

        Returns:
            `True` if the word is in the GADDAG, `False` if not.
        """
        return self._has(word)

    def contains(self, sub):
        """
        Find all words containing a substring.

        Args:
            sub: A substring to be searched for.

        Returns:
            A generator of all words found.
        """
        start_node = self.root.follow(sub[::-1])

        try:
            return self._crawl(start_node, sub)
        except TypeError:
            return set()

    def starts_with(self, prefix):
        """
        Find all words starting with a prefix.

        Args:
            prefix: A prefix to be searched for.

        Returns:
            A generator of all words found.
        """

        try:
            start_node = self.root.follow(prefix[::-1])["+"]
        except (KeyError, TypeError):
            return set()

        return self._crawl(start_node, prefix, wrapped=True)

    def ends_with(self, suffix):
        """
        Find all words ending with a suffix.

        Args:
            suffix: A suffix to be searched for.

        Returns:
            A generator of all words found.
        """

        start_node = self.root.follow(suffix[::-1])

        return self._crawl_end(start_node, suffix)

    def _has(self, word):
        """
        Check that a given word is in the GADDAG.

        Args:
            word: The word to be checked for.

        Returns:
            `True` if the word is in the GADDAG, `False` if not.
        """
        node = self.root

        try:
            for char in word[::-1]:
                node = node[char]
            node = node["+"]
        except KeyError:
            return False

        return True if node.is_end else False

    def _crawl(self, node, partial_word, found_words=None, wrapped=False):
        """
        Recursively search the GADDAG for all words, starting at a given node.

        Args:
            node: The node to start the search at.
            partial_word: The characters built up so far from traversing edges.
            wrapped: Has the node which signifies the start of the word
            been located (Default value = False)

        Returns:
            A generator of all words found.
        """

        if found_words is None:
            found_words = set()

        if node.is_end and ''.join(partial_word) not in found_words:
            found_words.add(''.join(partial_word))
            yield partial_word

        for char in node:
            next_node = node[char]

            if char == "+":
                for word in self._crawl(next_node, partial_word, found_words, True):
                    yield word
            else:
                new_partial_word = partial_word[:]
                if wrapped:
                    new_partial_word.append(char)
                else:
                    new_partial_word.insert(0, char)
                for word in self._crawl(next_node, new_partial_word, found_words, wrapped):
                    yield word

    def _crawl_end(self, node, partial_word):
        """
        Recursively search the GADDAG for all words, starting at a given node.

        This method does not follow "+" edges, which has the result that only
        words completed by prepended the followed edges are found, I.E., those
        which end with 'partial_word'.

        Args:
            node: The node to start the search at.
            partial_word: The characters built up so far from traversing edges.

        Returns:
            A generator of all words found.
        """
        try:
            if node["+"].is_end:
                yield partial_word
        except KeyError:
            pass
        except TypeError:
            return

        for char in node:
            if char != "+":
                next_node = node[char]
                new_partial_word = partial_word[:]
                new_partial_word.insert(0, char)
                for word in self._crawl_end(next_node, new_partial_word):
                    yield word

    # ------------------------------------------------------------------------------
    # Length limited interrogation

    def starts_with_no(self, prefix, no):
        """
        Find all words starting with a prefix up to given length.

        Args:
            prefix: A prefix to be searched for.
            no: Maximum length

        Returns:
            A generator of all words found.
        """

        try:
            start_node = self.root.follow(prefix[::-1])["+"]
        except (KeyError, TypeError):
            return set()

        return self._crawl_no(start_node, prefix, no, wrapped=True)

    def ends_with_no(self, suffix, no):
        """
        Find all words ending with a suffix up to given length.

        Args:
            suffix: A suffix to be searched for.
            no: Maximum length

        Returns:
            A generator of all words found.
        """

        start_node = self.root.follow(suffix[::-1])

        return self._crawl_end_no(start_node, suffix, no)

    def _crawl_no(self, *args, found_words=None, wrapped=False):
        """
        Recursively search the GADDAG for all words up to a given length
        starting at a given node.

        Args:
            args must contain:
                node: The node to start the search at.
                partial_word: The characters built up so far from traversing edges.
                no: Maximum length
            keyword parameters:
                found_words: List of words found so far
                wrapped: Has the node which signifies the start of the
                word been located (Default value = False)

        Returns:
            A generator of all words found.
        """
        node, partial_word, no = args

        if found_words is None:
            found_words = set()

        if node.is_end and ''.join(partial_word) not in found_words:
            found_words.add(''.join(partial_word))
            yield partial_word

        for char in node:
            next_node = node[char]

            if char == "+":
                for word in self._crawl_no(next_node, partial_word, no,
                                           found_words=found_words, wrapped=True):
                    if len(word) == no:
                        yield word
            else:
                if len(partial_word) < no:
                    new_partial_word = partial_word[:]
                    if wrapped:
                        new_partial_word.append(char)
                    else:
                        new_partial_word.insert(0, char)
                    for word in self._crawl_no(next_node, new_partial_word,
                                               no, found_words=found_words, wrapped=wrapped):
                        if len(word) == no:
                            yield word

    def _crawl_end_no(self, node, partial_word, no):
        """
        Recursively search the GADDAG for all words up to a given length
        starting at a given node.

        This method does not follow "+" edges, which has the result that only
        words completed by prepended the followed edges are found, I.E., those
        which end with 'partial_word'.

        Args:
            node: The node to start the search at.
            partial_word: The characters built up so far from traversing edges.
            no: Maximum length

        Returns:
            A generator of all words found.
        """
        try:
            if node["+"].is_end:
                yield partial_word
        except KeyError:
            pass
        except TypeError:
            return

        for char in node:
            if char != "+" and len(partial_word) < no:
                next_node = node[char]
                new_partial_word = partial_word[:]
                new_partial_word.insert(0, char)
                for word in self._crawl_end_no(next_node, new_partial_word, no):
                    if len(word) == no:
                        yield word

    # ------------------------------------------------------------------------------
    # Letter limited interrogation

    def contains_lett(self, sub, letters):
        """
        Find all words containing a substring using only given letters.

        Args:
            sub: A substring to be searched for.
            letters: list of allowed letters

        Returns:
            A generator of all words found as (start pos of sub, word.
        """

        start_node = self.root.follow(sub[::-1])
        if start_node is None:
            return set()

        try:
            return self._crawl_lett(start_node, sub, letters)
        except TypeError:
            return set()

    def starts_with_lett(self, prefix, letters):
        """
        Find all words starting with a prefix using only given letters.

        Args:
            prefix: A prefix to be searched for.
            letters: list of allowed letters

        Returns:
            A generator of all words found.
        """

        try:
            start_node = self.root.follow(prefix[::-1])["+"]
        except (KeyError, TypeError):
            return set()

        return self._crawl_lett(start_node, prefix, letters, wrapped=True)

    def ends_with_lett(self, suffix, letters):
        """
        Find all words ending with a suffix using only given letters.

        Args:
            suffix: A suffix to be searched for.
            letters: list of allowed letters

        Returns:
            A generator of all words found.
        """

        start_node = self.root.follow(suffix[::-1])

        return self._crawl_end_lett(start_node, suffix, letters)

    def _crawl_lett(self, *args, no=0, found_words=None, wrapped=False):
        """
        Recursively search the GADDAG for all words using only the given letters
        starting at a given node.

        Args:
            args must contain:
                node: The node to start the search at.
                partial_word: The characters built up so far from traversing edges.
                letters: list of allowed letters
            keyword parameters:
                no: Number of letters added as prefix (Default value = 0)
                found_words: List of words found so far (Default value = None)
                wrapped: Has the node which signifies the start of the word
                been located (Default value = False)

        Returns:
            A generator of all (no letters added as prefix, word) found.
        """

        node, partial_word, letters = args

        if found_words is None:
            found_words = set()

        if node.is_end and ''.join(partial_word) not in found_words:
            found_words.add(''.join(partial_word))
            yield no, partial_word

        for char in node:
            next_node = node[char]

            if char == "+":
                for word in self._crawl_lett(next_node, partial_word,
                                             letters, no=no, found_words=found_words, wrapped=True):
                    yield word

            elif letters and (char in letters or ' ' in letters):
                if wrapped:
                    new_partial_word = partial_word[:]
                    new_partial_word.append(char)
                    for word in self._crawl_lett(next_node, new_partial_word,
                                                 self.get_newlist(char, letters, letters), no=no,
                                                 found_words=found_words, wrapped=wrapped):
                        yield word
                else:
                    new_partial_word = partial_word[:]
                    new_partial_word.insert(0, char)
                    for word in self._crawl_lett(next_node, new_partial_word,
                                                 self.get_newlist(char, letters, letters), no=no + 1,
                                                 found_words=found_words, wrapped=wrapped):
                        yield word

    def _crawl_end_lett(self, node, partial_word, letters):
        """
        Recursively search the GADDAG for all words using only the given letters
        starting at a given node.

        This method does not follow "+" edges, which has the result that only
        words completed by prepended the followed edges are found, I.E., those
        which end with 'partial_word'.

        Args:
            node: The node to start the search at.
            partial_word: The characters built up so far from traversing edges.
            letters: list of allowed letters

        Returns:
            A generator of all words found.
        """
        try:
            if node["+"].is_end:
                yield partial_word
        except KeyError:
            pass
        except TypeError:
            return

        for char in node:
            if char != "+" and letters and char in letters:
                next_node = node[char]
                new_partial_word = partial_word[:]
                new_partial_word.insert(0, char)
                for word in self._crawl_end_lett(next_node, new_partial_word,
                                                 self.get_newlist(char, letters, True)):
                    yield word

    def contains_lett_patt(self, sub, letters=None, pattern=None):
        """
        Find all words containing a substring and subsequent pattern of letters.

        Args:
            sub: A substring to be searched for.
            letters: list of allowed letters,
            pattern: Dictionary of letters and position {pos:letter}
                    {no of chars to right of sub: letter}
                    0 means immediately next to right of sub

        Returns:
            A generator of all words found.
        """

        start_node = self.root.follow(sub[::-1])
        if start_node is None:
            return set()

        try:
            return self._crawl_lett_patt(start_node, sub, letters, pattern, no=0, pos=0)
        except TypeError:
            return set()

    def _crawl_lett_patt(self, *args, no=0,
                         pos=0, found_words=None, wrapped=False):
        """
        Recursively search the GADDAG for all words containing pattern of letters
        starting at a given node.

        Args:
            args must contain:
                node: The node to start the search at.
                partial_word: The characters built up so far from traversing edges.
                letters: list of allowed letters
                pattern: Dictionary of letters and position (Default value = None)
            keyword parameters:
                no: Number of letters added as prefix (Default value = 0)
                pos: No added as suffix (Default value = 0)
                found_words: List of words found so far (Default value = None)
                wrapped: Has the node which signifies the start of the word been
                located (Default value = False)

        Returns:
            A generator of all (no letters added as prefix, word) found.
        """
        node, partial_word, letters, pattern = args

        if found_words is None:
            found_words = set()

        if node.is_end and ''.join(partial_word) not in found_words:
            found_words.add(''.join(partial_word))
            yield no, partial_word

        for char in node:
            next_node = node[char]

            # Conditions required as tuple
            conditions = (not letters or (letters and (char in letters or ' ' in letters)),
                          pattern and pos in pattern,
                          pattern and pos in pattern and pattern[pos] == char)

            if char == "+":
                for word in self._crawl_lett_patt(next_node, partial_word, letters,
                                                  pattern, no=no, pos=pos,
                                                  found_words=found_words, wrapped=True):
                    yield word

            else:
                # Add letter after partial_word (no of characters after sub in pos)
                if wrapped and (conditions[2] or (not conditions[1] and conditions[0])):
                    new_partial_word = partial_word[:]
                    new_partial_word.append(char)
                    for word in self._crawl_lett_patt(next_node, new_partial_word,
                                                      self.get_newlist(char, letters,
                                                                       letters and not conditions[2]),
                                                      pattern, no=no,
                                                      pos=pos + 1, found_words=found_words,
                                                      wrapped=wrapped):
                        yield word
                # Add letter before partial_word (no of characters before sub in no)
                elif not wrapped and conditions[0]:
                    new_partial_word = partial_word[:]
                    new_partial_word.insert(0, char)
                    for word in self._crawl_lett_patt(next_node, new_partial_word,
                                                      self.get_newlist(char, letters, letters),
                                                      pattern, no=no + 1,
                                                      pos=pos, found_words=found_words,
                                                      wrapped=wrapped):
                        yield word

    def find_lett_patt(self, letters=None, pattern=None):
        """
        Find all words containing a pattern of letters.

        Args:
            letters: list of allowed letters,
            pattern: A text pattern string of fixed length
                     - for any letter eg "---a--"

        Returns:
            A generator of all words found.
        """
        start_node = self.root
        if start_node is None:
            return set()

        for char in pattern:
            if char.isalpha():
                letters.append(char)

        try:
            return self._crawl_find_lett_patt(start_node, [], letters, pattern)
        except TypeError:
            return set()

    def _crawl_find_lett_patt(self, node, partial_word, letters, pattern, found_words=None, wrapped=False):
        """
        Recursively search the GADDAG for all words containing pattern of letters
        starting at a given node.

        Args:
            args must contain:
                node: The node to start the search at.
                partial_word: The characters built up so far from traversing edges.
                letters: list of allowed letters
                pattern: Fixed length pattern as string
            keyword parameters:
                found_words: List of words found so far (Default value = None)
                wrapped: Has the node which signifies the start of the word been

        Returns:
            A generator of all (no letters added as prefix, word) found.
        """

        if found_words is None:
            found_words = set()

        if node.is_end and ''.join(partial_word) not in found_words:
            # print(partial_word, pattern, self.check_pattern(partial_word, pattern))
            if self.check_pattern(partial_word, pattern):
                found_words.add(''.join(partial_word))
                yield partial_word

        for char in node:
            next_node = node[char]

            if char == "+":
                for word in self._crawl_find_lett_patt(next_node, partial_word, letters, pattern,
                                                       found_words=found_words, wrapped=True):
                    yield word
            elif char in letters and len(partial_word) < len(pattern):
                new_partial_word = partial_word[:]
                if wrapped:
                    new_partial_word.append(char)
                    new_letters = self.get_newlist(char, letters, letters)
                else:
                    new_partial_word.insert(0, char)
                    new_letters = self.get_newlist(char, letters, letters)
                for word in self._crawl_find_lett_patt(next_node, new_partial_word, new_letters, pattern,
                                                       found_words=found_words, wrapped=wrapped):
                    yield word

    @staticmethod
    def check_pattern(partial_word, pattern):
        check = True
        if len(partial_word) != len(pattern):
            return False
        for i in range(len(pattern)):
            if pattern[i] != "-" and partial_word[i] != pattern[i]:
                check = False
                break
        return check

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
            else:
                new_list.remove(' ')
        return new_list


class Node:
    """A node in a GADDAG."""

    def __init__(self, end=False):
        self._edges = {}
        self._end = end

    def __str__(self):
        return "[{}] {}".format(", ".join(sorted([edge for edge in self])), self._end)

    def __iter__(self):
        for char in self._edges:
            yield char

    def __len__(self):
        return len(self._edges)

    def __contains__(self, char):  # defines 'in' for a node
        return char in self._edges

    def __getitem__(self, char):  # indexing allows self[char]
        return self._edges[char]

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented

        if self.edges != other.edges or self.is_end != other.is_end:
            return False

        for child in self:
            if self[child] != other[child]:
                return False

        return True

    @property
    def edges(self):
        """Return the edges of this node."""
        return {char for char in self} or None

    @property
    def is_end(self):
        """Return `True` if this node is an end node, `False` otherwise."""
        return self._end

    @property
    def end(self):
        """ Return `True` if this node is an end node, `False` otherwise."""
        return self._end

    @end.setter
    def end(self, value):
        """ Set `True` if this node is an end node, `False` otherwise."""
        self._end = value

    def follow(self, chars):
        """
        Traverse the GADDAG to the node at the end of the given characters.

        Args:
            chars: An string of characters to traverse in the GADDAG.

        Returns:
            The Node which is found by traversing the tree.
        """
        node = self
        for char in chars:
            try:
                node = node[char]
            except KeyError:
                return None

        return node

    def set_edge(self, char, dst):
        """
        Set an edge of this node.

        Args:
            char: Character for the edge to be set.
            dst: Node that the new edge will lead to.
        """
        self._edges[char] = dst

    def add_edge(self, char, dst=None, end=False):
        """
        Add an edge to this node.

        Args:
            char: Character for the edge to be added.
            dst: Node that the new edge will lead to.
            end: End node if dst is None

        Returns:
            The new node or, if the edge already exists, the node found by
            following that edge.
        """
        if dst is None:
            dst = Node(end)

        if char in self:
            return self[char]

        self.set_edge(char, dst)
        return dst

    def add_path(self, chars):
        """
        Add a path extending from this node with the edges in chars.

        For example, adding "foo" to a node will lead to the following structure:
            (this node) -'f'-> (next node) -'o'-> (next node) -'o'-> (next node)

        Where (next node) is a new node or, if the edge already exists, the node
        found by following that edge.

        Args:
            chars: A sequence of characters for edges on the path.

        Returns:
            The final node in the path.
        """
        node = self
        for char in chars:
            node = node.add_edge(char)

        return node

    def add_end(self, char):
        """
        Create an end node on the edge 'char'.

        If the edge 'char' already exists, the node found by
        folowing that edge is marked as an end node.

        Args:
            char: The edge to create the end node on.
        """
        if char in self:
            self[char].end = True
        else:
            self.add_edge(char, end=True)


class OpenStream(io.BytesIO):
    """ A Stream class that allows event processing
        during long operations """

    process_interval = 50000

    def __init__(self, filename=None, mode=''):
        super(OpenStream, self).__init__()
        if filename is not None:
            self.handle = open(filename, mode)
        self.count = 0
        self.previous = 0

    def open(self, filename=None, mode=''):
        """ Open stream """
        if filename is not None:
            self.handle = open(filename, mode)
        return self

    def read(self, no_bytes=1):
        """ Read data with event processing """

        self.count += no_bytes
        if (self.count - self.previous) >= OpenStream.process_interval:
            self.previous = self.count
            # APP.processEvents()
            time.sleep(0.01)
        return self.handle.read(no_bytes)

    def close(self):
        """ Close stream """
        self.handle.close()

    def reset(self):
        """ Reset counters """
        self.count = 0
        self.previous = 0


class SafeUnpickler(pickle.Unpickler):
    """ Subclass of pickle.Unpickler that overrides find_class method
        Allows load of pickled data from any module without
        necessity of importing all pickled classes into that module """

    _unpickle_map_safe = {
        # all possible and allowed (!) classes & upgrade paths
        # (module, class) as in pickled file: actual class reference
        (__name__, 'GADDAG'): GADDAG,
        (__name__, 'Node'): Node,
        ('__main__', 'GADDAG'): GADDAG,
        ('__main__', 'Node'): Node,
        ('pygaddag', 'Node'): Node,
        ('testgaddag', 'Node'): Node,
    }

    def find_class(self, modname, clsname):
        """ Overriden find_class method """

        print("DEBUG unpickling: %(modname)s . %(clsname)s" % locals())
        try:
            return SafeUnpickler._unpickle_map_safe[(modname, clsname)]
        except KeyError:
            raise pickle.UnpicklingError(
                "%(modname)s . %(clsname)s not allowed" % locals())

# Create and save GADDAG from text file
# graph = GADDAG()
# graph.create_from_file("francais\joueur0.txt")
# graph.save("francais\joueur0.p
