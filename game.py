"""
author: Josyp Dachuk
created: 07/06/2019
last modified: 07/08/2019
"""

import random
import tkinter as tk
from PIL import Image, ImageTk


class Const:
    """Constants for Snake Game"""
    SPEED_INCREASE = 50
    DELAY = 300
    MIN_DELAY = 50
    SQUARE_SIZE = 20
    NUM_OF_SQUARES = 30

    G_F_S = 20  # Game Board font size
    G_F = ('no font', G_F_S)  # Game Board font

    G_B_W = NUM_OF_SQUARES * SQUARE_SIZE  # Game Board width
    G_B_H = NUM_OF_SQUARES * SQUARE_SIZE  # Game Board height
    G_B_BG = '#5B5B5B'  # Game Board background color

    MIN_RAND_POS = 0
    MAX_RAND_POS = G_B_W // SQUARE_SIZE - 1

    S_F_S = 10  # Score Board font size
    S_F = ('no font', S_F_S)  # Score Board font

    S_B_W = 120  # Score Board width
    S_B_H = G_B_H  # Score Board height
    S_B_BG = '#3A3A3A'  # Score Board background

    RIGHT_KEY = 'Right'
    DOWN_KEY = 'Down'
    LEFT_KEY = 'Left'
    UP_KEY = 'Up'
    DIRECTION_KEYS = [RIGHT_KEY, DOWN_KEY, LEFT_KEY, UP_KEY]


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

    def __mul__(self, other):
        if isinstance(other, int):
            return Position(self.x * other, self.y * other)
        elif isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y)

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y


class Move:

    def __init__(self, move_x, move_y):
        self.move_x = move_x
        self.move_y = move_y

    def __mul__(self, other):
        if isinstance(other, int):
            return Move(self.move_x * other, self.move_y * other)
        elif isinstance(other, Move):
            return Move(self.move_x * other.move_x, self.move_y * other.move_y)


class Direction(Move):
    NORTH = Move(0, -1)
    EAST = Move(1, 0)
    SOUTH = Move(0, 1)
    WEST = Move(-1, 0)


class GameObject:

    def __init__(self, canvas, name, position):
        self._canvas = canvas
        self.name = name
        self.position = position
        self.image = None
        self.id = -1

    def draw(self):
        self.id = self._canvas.create_image(self.position.x, self.position.y,
                                            image=self.image, anchor=tk.NW, tag=self.name)

    def move(self, move):
        if self.id != -1:
            self._canvas.move(self.id, move.move_x, move.move_y)
            self.position = self.position + move

    def delete(self):
        if self.id != -1:
            self._canvas.delete(self.id)
            self.id = -1


class SnakeHead(GameObject):

    def __init__(self, canvas, position):
        super().__init__(canvas, 'head', position)
        self.image = ImageTk.PhotoImage(Image.open('images/head.png'))


class SnakeTail(GameObject):

    def __init__(self, canvas, position):
        super().__init__(canvas, 'tail', position)
        self.image = ImageTk.PhotoImage(Image.open('images/tail.png'))


class Apple(GameObject):

    def __init__(self, canvas):
        rx = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
        ry = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
        super().__init__(canvas, 'apple', Position(rx, ry))
        self.image = ImageTk.PhotoImage(Image.open('images/apple.png'))

        self.draw()


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


class GameBoard(tk.Canvas):
    """Game Board"""

    def __init__(self):
        """Initialize game board"""
        super().__init__(width=Const.G_B_W, height=Const.G_B_H,
                         background=Const.G_B_BG)

    def check_apple_in_pos(self, position):
        return 'apple' in self.gettags(self.find_in_position(position))

    def find_in_position(self, position):
        return self.find_overlapping(position.x, position.y, position.x, position.y)


class StatisticBoard(tk.Canvas):
    """Score Board"""

    def __init__(self):
        """Initialize Score Board"""
        self.score = 0
        self.level = 0
        self.high_score = 0
        self.display_level = True

        super().__init__(width=Const.S_B_W, height=Const.S_B_H,
                         background=Const.S_B_BG)

        self.create_objects()

    def create_objects(self):
        """Creates Objects"""
        if self.display_level:
            self.create_text(10, 10, text=f'Level: {self.level}', font=Const.S_F,
                             fill='white', anchor=tk.W, tag='level')
        self.create_text(10, 20, text=f'Score: {self.score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='score')
        self.create_text(10, 30, text=f'High Score: {self.high_score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='h_score')

    def update_level(self, level):
        """Updates level score"""
        if self.display_level:
            self.level = level
            self.itemconfigure('level', text=f'Level: {self.level}')

    def update_score(self, score):
        """Updates score"""
        self.score = score
        self.itemconfigure('score', text=f'Score: {self.score}')

    def update_high_score(self, h_score):
        """Updates high score"""
        self.high_score = h_score
        self.itemconfigure('h_score', text=f'High Score: {self.high_score}')

    def update_info(self, level, score, h_score):
        """Updates all game info"""
        self.update_level(level)
        self.update_score(score)
        self.update_high_score(h_score)

    def switch_level_system(self):
        self.display_level = not self.display_level
        self.level = 1
        if self.display_level:
            self.create_text(10, 10, text=f'Level: {self.level}', font=Const.S_F,
                             fill='white', anchor=tk.W, tag='level')
        else:
            self.delete(self.find_withtag('level'))


class SnakeGame(tk.Frame):

    class ControlKeys:
        """Keys"""
        SPACE_KEY = 'space'  # Pause
        RETURN_KEY = 'Return'  # Replay
        SHIFT_L_KEY = 'Shift_L'  # Turn on/off level system
        SHIFT_R_KEY = 'Shift_R'  # Turn on/off level system

    def __init__(self):
        super().__init__()

        self.master.title('Snake Game')

        self.statistic_board = StatisticBoard()
        self.board = GameBoard()

        self.level = 1
        self.score = 0
        self.high_score = 0

        self.apples = []
        self.snake = Snake(self, self.board)

        self.paused = False
        self.in_game = True
        self.level_system = True

        self.bind_all('<Key>', self.on_key_pressed)

        self.statistic_board.grid(column=0, row=0)
        self.board.grid(column=1, row=0)

        self.init_game()

    def init_game(self):
        """Initialize game objects and starts game"""
        self.snake.draw()
        self.locate_apples()
        self.statistic_board.update_info(self.level, self.score, self.high_score)

        self.after(Const.DELAY, self.on_timer)

    def locate_apples(self):
        """Locating an apple"""
        while len(self.apples) < self.level:
            apple = Apple(self.board)
            self.apples.append(apple)

    def on_timer(self):
        """On timer tick function"""
        if not self.paused and self.in_game:
            self.snake.make_turn()
            self.check_level_up()

            delay = Const.DELAY - (self.level - 1) * Const.SPEED_INCREASE
            if delay >= Const.MIN_DELAY:
                self.after(delay, self.on_timer)
            else:
                self.after(Const.MIN_DELAY, self.on_timer)

    def delete_apple(self, apple):
        """Removes apple"""
        self.apples.remove(apple)
        apple.delete()

    def check_level_up(self):
        """Check for level up"""
        if self.score / self.level > 10 and self.level_system:
            self.level += 1
            self.statistic_board.update_level(self.level)
            self.locate_apples()

    def update_score(self):
        """Updates score"""
        self.score += 1
        self.statistic_board.update_score(self.score)

    def replay(self):
        """Replay"""
        self.board.delete(tk.ALL)
        self.level = 1
        self.score = 0
        self.in_game = True

        self.snake = Snake(self, self.board)
        self.apples = []

        self.init_game()

    def switch_level_system(self):
        self.level_system = not self.level_system
        self.statistic_board.switch_level_system()

    def pause(self):
        """Pause the game"""
        self.paused = True
        self.board.create_text(self.board.winfo_width() / 2, self.board.winfo_height() / 2,
                               text='Pause', fill='white', tag='pause', font=Const.G_F)

    def unpause(self):
        """Unpause the game"""
        self.paused = False
        pause = self.board.find_withtag('pause')
        self.board.delete(pause)
        self.on_timer()

    def on_key_pressed(self, event):
        """Key pressed listener"""
        key = event.keysym

        if self.in_game:

            # Move directions
            if key in Const.DIRECTION_KEYS:
                self.snake.change_direction(key)

            # Pause
            elif key == self.ControlKeys.SPACE_KEY:
                if not self.paused:
                    self.pause()
                else:
                    self.unpause()
        else:
            if key == self.ControlKeys.RETURN_KEY:
                self.replay()
            elif key == self.ControlKeys.SHIFT_L_KEY or key == self.ControlKeys.SHIFT_R_KEY:
                self.switch_level_system()

    def game_over(self):
        """Game Over"""
        self.in_game = False

        if self.score > self.high_score:
            self.high_score = self.score
            self.statistic_board.update_high_score(self.high_score)

        font_size = Const.G_F_S
        font = Const.G_F

        self.board.create_text(self.board.winfo_width() / 2, self.board.winfo_height() / 2 - 4 * font_size,
                               text=f'Game Over!', fill='white', font=font)
        self.board.create_text(self.board.winfo_width() / 2, self.board.winfo_height() / 2 - 2 * font_size,
                               text=f'Score: {self.score}', fill='white', font=font)
        self.board.create_text(self.board.winfo_width() / 2, self.board.winfo_height() / 2 - 1 * font_size,
                               text=f'High Score: {self.high_score}', fill='white', font=font)
        self.board.create_text(self.board.winfo_width() / 2, self.board.winfo_height() / 2 + 3 * font_size,
                               text='Play again? Press ENTER!', fill='white', font=font)


if __name__ == '__main__':
    root = tk.Tk()
    SnakeGame()
    root.mainloop()
