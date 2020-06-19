import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        try:
            i, j = cell
        except Exception as ex:
            print(cell)
            raise ex
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.cells if self.count == len(self.cells) else set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1 • The function should mark the cell as one of the moves made in the game.
        self.moves_made.add(cell)

        # 2 • The function should mark the cell as a safe cell, updating any sentences that contain the cell as well.
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        # 3 • The function should add a new sentence to the AI’s knowledge base, based on the value of cell and count, to indicate that count of the cell’s neighbors are mines. Be sure to only include cells whose state is still undetermined in the sentence.
        x, y = cell
        adjacent_cells = {
            (i, j)
            for i in range(x-1, x+1+1)
            for j in range(y-1, y+1+1)
            if 0 <= i and i < self.height
            and 0 <= j and j < self.width
        }
        adjacent_cells -= {cell}  # just to be safe
        # exclude clicked cells
        unclicked_adjacent_cells = adjacent_cells - self.moves_made  

        self.knowledge.append(
            Sentence(unclicked_adjacent_cells, count))

        # "Updating" involves checking each sentence for known mines / safes, and marking them on all sentences.
        def update_knowledge(sentence_list):
            unmarked_mines = set()
            unmarked_safes = set()

            # accumulate unmarked mines and safes
            for sentence in sentence_list:
                unmarked_mines |= sentence.known_mines()
                unmarked_safes |= sentence.known_safes()

            # return the fact that no changes are needed
            if len(unmarked_mines) + len(unmarked_safes) == 0:
                return False

            # update knowledge
            self.mines |= unmarked_mines
            self.safes |= unmarked_safes
            for mine in unmarked_mines:
                self.mark_mine(mine)
            for safe in unmarked_safes:
                self.mark_safe(safe)

            # return the fact that changes have been made
            return True

        # Keep looping until knowledge is updated completely.
        while True:
            # 4 • If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines, then the function should do so.

            is_changes_made = update_knowledge(self.knowledge)

            # no changes made means loop can stop
            if is_changes_made is False:
                break

        # 5 • If, based on any of the sentences in self.knowledge, new sentences can be inferred (using the subset method described in the Background), then those sentences should be added to the knowledge base as well.
            # employing subset method with each sentence pair permutation
            permutations = itertools.permutations(self.knowledge, 2)
            new_sentences = []
            for left, right in permutations:
                if left.cells < right.cells:
                    new_sentence = Sentence(
                        right.cells - left.cells,
                        right.count - left.count
                    )
                    new_sentences.append(new_sentence)
                # left.cells == right.cells can be ignored because the result will be empty set with 0 count

            self.knowledge += new_sentences
            # only new sentences need to be updated
            is_changes_made = update_knowledge(new_sentences)

            # no changes made means loop can stop
            if is_changes_made is False:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        possible_set = (self.safes - self.moves_made)
        return next(iter(possible_set)) if len(possible_set) > 0 else None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possible_set = (
            set(itertools.product(range(self.height), range(self.width)))
            - self.moves_made
            - self.mines
        )

        return random.sample(possible_set, 1)[0]