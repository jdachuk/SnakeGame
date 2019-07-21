"""
author: edacjos
created: 7/10/19
last modified: 07/13/2019
"""


class Move:

    def __init__(self, move_x, move_y):
        self.move_x = move_x
        self.move_y = move_y

    def __mul__(self, other):
        if isinstance(other, int):
            return Move(self.move_x * other, self.move_y * other)
        elif isinstance(other, Move):
            return Move(self.move_x * other.move_x, self.move_y * other.move_y)

    def __str__(self):
        return f'{self.move_x, self.move_y}'


class Direction(Move):
    NORTH = Move(0, -1)
    EAST = Move(1, 0)
    SOUTH = Move(0, 1)
    WEST = Move(-1, 0)

    NORTH_EAST = Move(1, -1)
    SOUTH_EAST = Move(1, 1)
    SOUTH_WEST = Move(-1, 1)
    NORTH_WEST = Move(-1, -1)


class Const:
    """Constants for Snake Game"""
    SPEED_INCREASE = 50
    DELAY = 300
    MIN_DELAY = 50
    AI_DELAY = 64
    MIN_AI_DELAY = 1
    MAX_AI_DELAY = 256
    SQUARE_SIZE = 15
    NUM_OF_SQUARES = 40

    G_F_S = 20  # Game Board font size
    G_F = ('no font', G_F_S)  # Game Board font

    G_B_W = NUM_OF_SQUARES * SQUARE_SIZE  # Game Board width
    G_B_H = NUM_OF_SQUARES * SQUARE_SIZE  # Game Board height
    G_B_BG = '#5B5B5B'  # Game Board background color

    P_B_W = NUM_OF_SQUARES * SQUARE_SIZE
    P_B_H = NUM_OF_SQUARES * SQUARE_SIZE

    MIN_RAND_POS = 0
    MAX_RAND_POS = G_B_W // SQUARE_SIZE - 1

    S_F_S = 10  # Score Board font size
    S_F = ('no font', S_F_S)  # Score Board font

    S_B_W = 160  # Score Board width
    S_B_H = G_B_H  # Score Board height
    S_B_BG = '#3A3A3A'  # Score Board background

    RIGHT_KEY = 'Right'
    DOWN_KEY = 'Down'
    LEFT_KEY = 'Left'
    UP_KEY = 'Up'
    DIRECTION_KEYS = [RIGHT_KEY, DOWN_KEY, LEFT_KEY, UP_KEY]
    DIRECTIONS = [
                Direction.NORTH, Direction.NORTH_EAST, Direction.EAST, Direction.SOUTH_EAST,
                Direction.SOUTH, Direction.SOUTH_WEST, Direction.WEST, Direction.NORTH_WEST
            ]

    POPULATION_SIZE = 1000
    MUTATION_RATE = .01
    CROSSOVER_RATE = .8
    MU, SIGMA = 0., 1.
    VERSION = 1.0


class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        if isinstance(other, Position):
            return Move(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        if isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y)
        elif isinstance(other, Move):
            return Position(self.x + other.move_x, self.y + other.move_y)
        elif isinstance(other, int):
            return Position(self.x + other, self.y + other)

    def __mul__(self, other):
        if isinstance(other, int):
            return Position(self.x * other, self.y * other)
        elif isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'({self.x}, {self.y})'
