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
    DOT_SIZE = 20

    G_F_S = 20  # Game Board font size
    G_F = ('no font', G_F_S)  # Game Board font

    G_B_W = 30 * DOT_SIZE  # Game Board width
    G_B_H = 30 * DOT_SIZE  # Game Board height
    G_B_BG = '#5B5B5B'  # Game Board background color

    MIN_RAND_POS = 0
    MAX_RAND_POS = G_B_W // DOT_SIZE - 1

    S_F_S = 10  # Score Board font size
    S_F = ('no font', S_F_S)  # Score Board font

    S_B_W = 120  # Score Board width
    S_B_H = G_B_H  # Score Board height
    S_B_BG = '#3A3A3A'  # Score Board background


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


class Direction:
    UP = Move(0, -1)
    DOWN = Move(0, 1)
    LEFT = Move(-1, 0)
    RIGHT = Move(1, 0)


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
        rx = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.DOT_SIZE
        ry = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.DOT_SIZE
        super().__init__(canvas, 'tail', Position(rx, ry))
        self.image = ImageTk.PhotoImage(Image.open('images/apple.png'))


class Snake:
    def __init__(self, canvas):
        self._canvas = canvas

        self._head = SnakeHead(canvas, Position(5, 5) * Const.DOT_SIZE)
        self._tail = [
            SnakeTail(canvas, Position(3, 5) * Const.DOT_SIZE),
            SnakeTail(canvas, Position(4, 5) * Const.DOT_SIZE)
        ]

        self.direction = Direction.RIGHT
        self.move = self.direction * Const.DOT_SIZE

        self.alive = True

    def draw(self):
        self._head.draw()
        for tail in self._tail:
            tail.draw()

    def make_turn(self):
        self.check_collisions()
        self.check_apple_collision()

        if self.alive:
            for idx in range(len(self._tail)):
                c1 = self._tail[idx].position

                try:
                    c2 = self._tail[idx + 1].position
                except IndexError:
                    c2 = self._head.position

                move = c2 - c1
                self._tail[idx].move(move)

            self.move = self.direction * Const.DOT_SIZE
            self._head.move(self.move)

    def check_apple_collision(self):
        apples = self._canvas.apples

        for apple in apples:
            apple_pos = apple.position
            if apple_pos == self._head.position:
                self._canvas.update_score()
                self._canvas.delete_apple(apple)

                tail = SnakeTail(self._canvas, apple_pos)
                tail.draw()
                self._tail.append(tail)

                self._canvas.locate_apples()

    def check_collisions(self):
        """Check collisions with snake tail or borders"""
        for tail in self._tail:
            if tail.position == self._head.position:
                self.alive = False
                self._canvas.game_over()

        if self._head.position.x < 0 or \
                self._head.position.x > Const.G_B_W - Const.DOT_SIZE or \
                self._head.position.y < 0 or \
                self._head.position.y > Const.G_B_H - Const.DOT_SIZE:
            self.alive = False
            self._canvas.game_over()

    @property
    def move_x(self):
        return self.move.move_x

    @property
    def move_y(self):
        return self.move.move_y


class GameBoard(tk.Canvas):
    """Game Board"""

    class ControlKeys:
        """Keys"""
        # In-game controls
        LEFT_KEY = 'Left'  # Move left
        RIGHT_KEY = 'Right'  # Move right
        UP_KEY = 'Up'  # Move up
        DOWN_KEY = 'Down'  # Move down
        SPACE_KEY = 'space'  # Pause
        # Out of game controls
        RETURN_KEY = 'Return'  # Replay
        SHIFT_L_KEY = 'Shift_L'  # Turn on/off level system
        SHIFT_R_KEY = 'Shift_R'  # Turn on/off level system

    def __init__(self, score_board):
        """Initialize game board"""
        # Initial data
        # Game data
        self.in_game = True
        self.paused = False
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.level_system = True  # Enable or disable level system in the game

        # Moves data
        self.snake = Snake(self)
        self.apples = []
        # End of initial data

        self.score_board = score_board

        super().__init__(width=Const.G_B_W, height=Const.G_B_H,
                         background=Const.G_B_BG, highlightthickness=0)

        # Bind controls
        self.bind_all('<Key>', self.on_key_pressed)

        self.init_game()

    def init_game(self):
        """Initialize game objects and starts game"""
        self.snake.draw()
        self.locate_apples()
        try:
            self.score_board.update_info(self.level, self.score, self.high_score)
        except AttributeError:
            print('Score board is not defined!')

        self.after(Const.DELAY, self.on_timer)

    def locate_apples(self):
        """Locating an apple"""
        while len(self.apples) < self.level:
            apple = Apple(self)
            apple.draw()
            self.apples.append(apple)

    def delete_apple(self, apple):
        """Removes apple"""
        self.apples.remove(apple)
        apple.delete()

    def on_key_pressed(self, event):
        """Key pressed listener"""
        key = event.keysym

        if self.in_game:

            # Move directions
            if key == self.ControlKeys.LEFT_KEY and self.snake.move_x == 0:
                self.snake.direction = Direction.LEFT
            elif key == self.ControlKeys.RIGHT_KEY and self.snake.move_x == 0:
                self.snake.direction = Direction.RIGHT
            elif key == self.ControlKeys.UP_KEY and self.snake.move_y == 0:
                self.snake.direction = Direction.UP
            elif key == self.ControlKeys.DOWN_KEY and self.snake.move_y == 0:
                self.snake.direction = Direction.DOWN

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

    def update_score(self):
        """Updates score"""
        self.score += 1
        try:
            self.score_board.update_score(self.score)
        except AttributeError:
            print('Score board is not defined!')

    def game_over(self):
        """Game Over"""
        self.in_game = False

        if self.score > self.high_score:
            self.high_score = self.score
        try:
            self.score_board.update_high_score(self.high_score)
        except AttributeError:
            print('Score board is not defined!')

        font_size = Const.G_F_S
        font = Const.G_F

        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 - 4 * font_size,
                         text=f'Game Over!', fill='white', font=font)
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 - 2 * font_size,
                         text=f'Score: {self.score}', fill='white', font=font)
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 - 1 * font_size,
                         text=f'High Score: {self.high_score}', fill='white', font=font)
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2 + 3 * font_size,
                         text='Play again? Press ENTER!', fill='white', font=font)

    def pause(self):
        """Pause the game"""
        self.paused = True
        self.create_text(self.winfo_width() / 2, self.winfo_height() / 2,
                         text='Pause', fill='white', tag='pause', font=Const.G_F)

    def unpause(self):
        """Unpause the game"""
        self.paused = False
        pause = self.find_withtag('pause')
        self.delete(pause)
        self.on_timer()

    def check_level_up(self):
        """Check for level up"""
        if self.score / self.level > 10 and self.level_system:
            self.level += 1
            try:
                self.score_board.update_level(self.level)
            except AttributeError:
                print('Score board is not defined!')
            self.locate_apples()

    def replay(self):
        """Replay"""
        self.delete(tk.ALL)
        self.level = 1
        self.score = 0
        self.in_game = True

        self.snake = Snake(self)
        self.apples = []

        self.init_game()

    def switch_level_system(self):
        self.level_system = not self.level_system
        try:
            self.score_board.switch_level_system()
        except AttributeError:
            print('Score board is not defined!')


class ScoreBoard(tk.Canvas):
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

    def __init__(self):
        super().__init__()

        self.master.title('Snake Game')

        self.score_board = ScoreBoard()
        self.board = GameBoard(score_board=self.score_board)

        self.score_board.grid(column=0, row=0)
        self.board.grid(column=1, row=0)


if __name__ == '__main__':
    root = tk.Tk()
    SnakeGame()
    root.mainloop()
