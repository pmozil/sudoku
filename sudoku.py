from random import randint, sample

CLEAR = "\033c"
RED = "\033[0;031m"
GREEN = "\033[0;32m"
BLUE = "\033[1;34m"
RESET = "\033[0;0m"


class Tile:
    """
    A sudoku tile class

    Attributes:
    ----------
    preset: bool
        tile is preset, thus unchangeable

    val: int
        tile value

    ch: str
        char representation of value, is ' ' when not 1 <= val <= 9

    max_val: int
        tile's max value

    Methods
    -------
    set_val(val=0):
        sets tile value

    toggle_preset():
        toggles the tile's preset flag
    """

    def __init__(self, preset: bool = False, val: int = 0, max_val=9) -> None:
        """
        Constructs all the necessary attributes for the tile object.

        Parameters
        ----------
        preset: bool
            a bool to show whether the tile is preset

        val: int
            tile's value
        """
        self.preset = preset
        self.max_val = max_val
        if not 0 <= val <= max_val:
            raise ValueError
        else:
            self.val = val
            self.ch = (" " if max_val < 10 else "  ") if val == 0 else str(val)

    def toggle_preset(self):
        """
        Toggles the tile's preset flag
        """
        self.preset = not self.preset

    def set_val(self, val: int = 0) -> None:
        """
        Set tile value

        Parameters
        ----------
        val: int
            tile's value
        """
        if not self.preset or not 0 <= val <= self.max_val:
            self.val = val
            self.ch = " " if val == 0 else str(val)
        else:
            raise ValueError

    @property
    def value(self) -> int:
        """Getter for the tile's value"""
        return self.val

    @value.setter
    def value(self, val: int):
        """Setter for the tile's value"""
        if not self.preset or not 0 <= val <= self.max_val:
            self.val = val
            self.ch = " " if val == 0 else str(val)
        else:
            raise ValueError


class Grid:
    """
    A sudoku board class

    Attributes
    ----------
    board: [[Tile]]
        a representation of the board

    size: int
        size of a square, it will be changed if it isn't a perfect square

    solved:
        solved board

    Methods
    -------
    generate():
        Generate a board

    set_at_coords(y=0, x=0, val=0):
        Set a value at x, y

    reset():
        Reset board to the start position

    clear():
        Clear the board

    print_board():
        Print the board

    print_solved():
        Print the solved board

    is_finished():
        Returns a bool that shows whether there are any 0s on the board
    """

    def __init__(self: "Grid", size: int = 4) -> None:
        """
        Constructs all the necessary attributes for the tile object.

        Parameters
        ----------
        size: int
            size of a square, it will be changed if it isn't a perfect square
        """
        # Make size a perfect square, I'm too lazy to deal with anything else
        size = int(size**0.5) ** 2
        # Make an square array of size size
        self.size = size
        self.base = int(self.size**0.5)
        self.board = [
            [Tile(val=0, max_val=self.base) for _ in range(size)]
            for _ in range(size)
        ]
        self.solved = [
            [Tile(val=0, max_val=self.base) for _ in range(size)]
            for _ in range(size)
        ]
        self.finished = False
        self.generate()

    def __getitem__(self, k) -> Tile:
        """
        getitem for the board
        """
        return self.board[k[0]][k[1]]

    def generate(self) -> None:
        """
        Generate board
        """
        self.clear()
        shuffle = lambda x: sample(x, len(x))
        pattern = (
            lambda r, c: (self.base * (r % self.base) + r // self.base + c)
            % self.size
        )
        base_range = range(self.base)

        rows = [
            g * self.base + row
            for g in shuffle(base_range)
            for row in shuffle(base_range)
        ]

        columns = [
            g * self.base + column
            for g in shuffle(base_range)
            for column in shuffle(base_range)
        ]

        nums = shuffle(range(1, self.size + 1))

        board = [[nums[pattern(r, c)] for c in columns] for r in rows]

        self.solved = [[Tile(True, j, self.size) for j in i] for i in board]

        for i in range(self.size):
            for j in range(self.size):
                if randint(1, self.size * 2) > self.size:
                    self.board[i][j].value = board[i][j]
                    self.board[i][j].toggle_preset()

    def __setitem__(self, key: tuple[int, int], val: int = 0) -> None:
        """
        Set value at coordinates

        Parameters
        __________

        x: int
        y: int
        val: int
            value to be set
        """
        y, x = key
        bx = x // self.base
        by = y // self.base

        square = [
            element.val
            for row in self.board[bx * self.base : (bx + 1) * self.base]
            for element in row[by * self.base : (by + 1) * self.base]
        ]

        if not (
            val in [self.board[i][y] for i in range(self.size)]
            or val in [self.board[x][i] for i in range(self.size)]
            or val in square
            or self.board[x][y].preset
        ):
            self.board[x][y].set_val(val)
            self.finished = self.is_finished()
        else:
            raise ValueError

    def reset(self) -> None:
        """
        Reset the board to its base state
        """
        for i in range(self.size):
            for j in range(self.size):
                if not self.board[i][j].preset:
                    self.board[i][j].set_val(0)

    def clear(self) -> None:
        """
        Clear the board
        """
        for i in range(self.size):
            for j in range(self.size):
                self.board[i][j].preset = False
                self.board[i][j].set_val(0)

        for i in range(self.size):
            for j in range(self.size):
                self.solved[i][j].preset = False
                self.solved[i][j].set_val(0)

    def __str__(self) -> str:
        """
        Print the board
        """
        result = ""
        if self.size < 10:
            result += "\n" + "-" * (self.size * 4 + 1) + "\n"
        else:
            result += "\n" + "-" * ((self.size - 9) * 5 + 10) + "\n"
        for i in self.board:
            for j in i:
                result += "| "
                # These weird characters set the colour of the number
                if j.preset:
                    # If j is preset, then make it red
                    result += RED
                else:
                    # Else, make j blue
                    result += "\033[0;34m"
                # Print j itself
                if j.val < 10 and self.size > 10:
                    result += " " + j.ch + " "
                else:
                    result += j.ch + " "
                # Reset the colours
                result += RESET

            if self.size < 10:
                result += "|\n" + "-" * (self.size * 4 + 1) + "\n"
            else:
                result += "|\n" + "-" * (self.size * 5 + 1) + "\n"
        return result

    @property
    def solved_str(self) -> str:
        """
        Print the solved board
        """
        result = ""
        result += BLUE
        result += "Too hard? Poor you. Here's a pity kitty" + "\n"
        result += '''
         ,-""""""-.
      /\\j__/\\  (  \\`--.
      \\`@_@'/  _)  >--.`.
     _{.:Y:_}_{{_,'    ) )
    {_}`-^{_} ```     (_/
            
    ( Credits to https://ascii.co.uk/art/cats)
        '''
        result += RESET
        if self.size < 10:
            result += "\n" + "-" * (self.size * 4 + 1) + "\n"
        else:
            result += "\n" + "-" * ((self.size - 9) * 5 + 10) + "\n"
        for i in range(self.size):
            for j in range(self.size):
                result += "| "
                # These weird characters set the colour of the number
                if self.board[i][j].preset:
                    result += RED
                else:
                    result += BLUE
                # Print j itself
                cell = self.solved[i][j]
                if cell.val < 10 and self.size > 10:
                    result += " " + cell.ch + " "
                else:
                    result += cell.ch + " "
                # Reset the colours
                result += RESET

            if self.size < 10:
                result += "|\n" + "-" * (self.size * 4 + 1) + "\n"
            else:
                result += "|\n" + "-" * (self.size * 5 + 1) + "\n"
        return result

    @property
    def finished_str(self) -> str:
        """
        Print the solved board
        """
        result = "\033[1;32m"
        result += """
Congratulations on finishing the game!
Here's a congratulations kitty (it's the same as the pity kitty)
"""
        result += '''
         ,-""""""-.
      /\\j__/\\  (  \\`--.
      \\`@_@'/  _)  >--.`.
     _{.:Y:_}_{{_,'    ) )
    {_}`-^{_} ```     (_/
            
    ( Credits to https://ascii.co.uk/art/cats)
        '''
        result += RESET
        if self.size < 10:
            result += "\n" + "-" * (self.size * 4 + 1) + "\n"
        else:
            result += "\n" + "-" * ((self.size - 9) * 5 + 10) + "\n"
        for i in self.solved:
            for j in i:
                result += "| "
                # These weird characters set the colour of the number
                result += GREEN
                # Print j itself
                if j.val < 10 and self.size > 10:
                    result += " " + j.ch + " "
                else:
                    result += j.ch + " "
                # Reset the colours
                result += RESET

            if self.size < 10:
                result += "|\n" + "-" * (self.size * 4 + 1) + "\n"
            else:
                result += "|\n" + "-" * (self.size * 5 + 1) + "\n"
        return result

    def is_finished(self) -> bool:
        for i in self.board:
            for j in i:
                if j.val == 0:
                    return False
        return True


class Game:
    """
    The game's base class

    Attributes
    ----------
    grid: Grid
        A game grid

    Methods
    -------
        play():
            plays the game until finnish or exit
        help():
            prints help
    """

    def __init__(self):
        self.grid = Grid()

    def help(self):
        """
        Print help
        """
        print(
            """
Here's a list of commands:
    - help
    - setBoardSize size (please use a perfect square for the size)
    - regenBoard
    - setAtPosition x y value (could also be pos x y value)
    - printSolution
    - quit
"""
        )

    def play(self):
        """
        Start the game
        """
        print(CLEAR)

        print(
            """
Welcome to sudoku! Print help for help
        """
        )
        while True:
            print(self.grid)
            cmd = input(">>>")
            print(CLEAR)
            if cmd.lower().startswith("setboardsize"):
                self.grid = Grid(int(cmd.split()[1]))
                self.grid.generate()
            elif cmd.lower() == "regenboard":
                self.grid.generate()
            elif cmd.lower().startswith(
                "setatposition"
            ) or cmd.lower().startswith("pos"):
                vals = [int(i) for i in cmd.lower().split()[1:]]
                try:
                    self.grid[vals[0] - 1, vals[1] - 1] = vals[2]
                except ValueError:
                    print("Oops! This can't be done!")
                except IndexError:
                    print("Oh no! There's no square at this coordinate!")
                if self.grid.finished:
                    print(self.grid.finished_str)
                    exit()
            elif cmd.lower() == "printsolution":
                print(self.grid.solved_str)
            elif cmd.lower() == "quit":
                print("Thanks for playing!")
                exit()
            else:
                self.help()


if __name__ == "__main__":
    game = Game()
    game.play()
