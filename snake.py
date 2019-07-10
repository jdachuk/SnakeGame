"""
author: edacjos
created: 7/10/19
"""


from support import Const, Position, Direction
from game_objects import SnakeHead, SnakeTail


class Snake:

    def __init__(self, game, canvas):
        self.game = game
        self.canvas = canvas

        self.head = SnakeHead(canvas, Position(5, 5) * Const.SQUARE_SIZE)
        self.tail = [
            SnakeTail(canvas, Position(3, 5) * Const.SQUARE_SIZE),
            SnakeTail(canvas, Position(4, 5) * Const.SQUARE_SIZE)
        ]

        self.direction = Direction.EAST
        self.move = self.direction * Const.SQUARE_SIZE

        self.alive = True

    def draw(self):

        self.head.draw()
        for tail in self.tail:
            tail.draw()

    def make_turn(self):

        future_pos = Position(self.head_x, self.head_y) + self.direction * Const.SQUARE_SIZE

        self.check_collisions(future_pos)

        if self.alive:
            for idx in range(len(self.tail)):
                c1 = self.tail[idx].position

                try:
                    c2 = self.tail[idx + 1].position
                except IndexError:
                    c2 = self.head.position

                move = c2 - c1
                self.tail[idx].move(move)

            self.move = self.direction * Const.SQUARE_SIZE
            self.head.move(self.move)

        self.check_apple_collision(future_pos)

    def check_apple_collision(self, future_pos):

        for apple in self.game.apples:

            if apple.position == future_pos:
                self.game.update_score()
                self.game.delete_apple(apple)

                tail = SnakeTail(self.canvas, self.tail[-1].position)
                tail.draw()
                self.tail.append(tail)

                self.game.locate_apples()

    def check_collisions(self, future_pos):
        """Check collisions with snake tail or borders"""
        for tail in self.tail:
            if tail.position == self.head.position:
                self.alive = False
                self.canvas.game_over()

        if future_pos.x < 0 or future_pos.x > Const.G_B_W - Const.SQUARE_SIZE or \
                future_pos.y < 0 or future_pos.y > Const.G_B_H - Const.SQUARE_SIZE:
            self.alive = False
            self.game.game_over()

    def change_direction(self, new_direction):
        if new_direction == 'Left' and self.move_x == 0:
            self.direction = Direction.WEST
        elif new_direction == 'Right' and self.move_x == 0:
            self.direction = Direction.EAST
        elif new_direction == 'Up' and self.move_y == 0:
            self.direction = Direction.NORTH
        elif new_direction == 'Down' and self.move_y == 0:
            self.direction = Direction.SOUTH

    @property
    def move_x(self):
        return self.move.move_x

    @property
    def move_y(self):
        return self.move.move_y

    @property
    def head_x(self):
        return self.head.position.x

    @property
    def head_y(self):
        return self.head.position.y
