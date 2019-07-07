"""
author: Josyp Dachuk
created: 07/06/2019
last modified: 07/07/2019
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


class GameBoard(tk.Canvas):
    """Game Board"""

    class ControlKeys:
        """Keys"""
        LEFT_KEY = 'Left'  # Move left
        RIGHT_KEY = 'Right'  # Move right
        UP_KEY = 'Up'  # Move up
        DOWN_KEY = 'Down'  # Move down
        SPACE_KEY = 'space'  # Pause
        RETURN_KEY = 'Return'  # Replay

    def __init__(self, score_board):
        """Initialize game board"""
        # Initial data
        # Game data
        self.in_game = True
        self.paused = False
        self.score = 0
        self.high_score = 0
        self.level = 1

        # Moves data
        self.move_x = Const.DOT_SIZE
        self.move_y = 0
        self.move_s = (self.move_x, self.move_y)

        # Apple position (will be overwritten)
        self.apple_x = 0
        self.apple_y = 0

        # Images
        self.dot = None
        self.head = None
        self.apple = None
        self.load_images()
        # End of initial data

        self.score_board = score_board

        super().__init__(width=Const.G_B_W, height=Const.G_B_H,
                         background=Const.G_B_BG, highlightthickness=0)

        # Bind controls
        self.bind_all('<Key>', self.on_key_pressed)

        self.init_game()

    def init_game(self):
        """Initialize game objects and starts game"""
        self.create_objects()
        self.locate_apple()
        self.score_board.update_info(self.level, self.score, self.high_score)

        self.after(Const.DELAY, self.on_timer)

    def load_images(self):
        """Loading images"""
        try:
            self.dot = ImageTk.PhotoImage(Image.open('images/tail.png'))
            self.head = ImageTk.PhotoImage(Image.open('images/head.png'))
            self.apple = ImageTk.PhotoImage(Image.open('images/apple.png'))
        except IOError as e:
            print(e)
            self.quit()

    def create_objects(self):
        """Creates game objects on board"""
        # Create Snake
        self.create_image(5 * Const.DOT_SIZE, 5 * Const.DOT_SIZE,
                          image=self.head, anchor=tk.NW, tag='head')
        self.create_image(3 * Const.DOT_SIZE, 5 * Const.DOT_SIZE,
                          image=self.dot, anchor=tk.NW, tag='dot')
        self.create_image(4 * Const.DOT_SIZE, 5 * Const.DOT_SIZE,
                          image=self.dot, anchor=tk.NW, tag='dot')

    def locate_apple(self):
        """Locating an apple"""
        while len(self.find_withtag('apple')) < self.level:
            r = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS)
            self.apple_x = Const.DOT_SIZE * r

            r = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS)
            self.apple_y = Const.DOT_SIZE * r

            self.create_image(self.apple_x, self.apple_y, image=self.apple, anchor=tk.NW, tag='apple')

    def on_key_pressed(self, event):
        """Key pressed listener"""
        key = event.keysym

        if key == self.ControlKeys.LEFT_KEY and self.move_s[0] <= 0:
            self.move_x = -Const.DOT_SIZE
            self.move_y = 0
        elif key == self.ControlKeys.RIGHT_KEY and self.move_s[0] >= 0:
            self.move_x = Const.DOT_SIZE
            self.move_y = 0
        elif key == self.ControlKeys.UP_KEY and self.move_s[1] <= 0:
            self.move_x = 0
            self.move_y = -Const.DOT_SIZE
        elif key == self.ControlKeys.DOWN_KEY and self.move_s[1] >= 0:
            self.move_x = 0
            self.move_y = Const.DOT_SIZE
        elif key == self.ControlKeys.SPACE_KEY:
            if not self.paused:
                self.pause()
            else:
                self.unpause()
        elif key == self.ControlKeys.RETURN_KEY:
            if not self.in_game:
                self.replay()

    def on_timer(self):
        """On timer tick function"""
        if not self.paused:
            self.check_collisions()

            if self.in_game:
                self.check_level()
                self.check_apple_collisions()
                self.move_snake()

                delay = Const.DELAY - (self.level - 1) * Const.SPEED_INCREASE
                if delay >= Const.MIN_DELAY:
                    self.after(delay, self.on_timer)
                else:
                    self.after(Const.MIN_DELAY, self.on_timer)
            else:
                self.game_over()

    def check_collisions(self):
        """Check collisions with snake tail or borders"""
        dots = self.find_withtag('dot')
        head = self.find_withtag('head')

        x1, y1, x2, y2 = self.bbox(head)
        overlap = self.find_overlapping(x1, y1, x2, y2)

        for dot in dots:
            for over in overlap:
                if dot == over:
                    self.in_game = False
                    return

        if x1 < 0:
            self.in_game = False
            return
        if x1 > Const.G_B_W - Const.DOT_SIZE:
            self.in_game = False
            return
        if y1 < 0:
            self.in_game = False
            return
        if y1 > Const.G_B_H - Const.DOT_SIZE:
            self.in_game = False
            return

    def check_apple_collisions(self):
        """Checks collisions with apple"""
        apples = self.find_withtag('apple')
        head = self.find_withtag('head')

        x1, y1, x2, y2 = self.bbox(head)
        overlap = self.find_overlapping(x1, y1, x2, y2)

        for over in overlap:
            for apple in apples:
                if apple == over:
                    self.score += 1
                    self.score_board.update_score(self.score)

                    x, y = self.coords(apple)
                    self.delete(apple)
                    self.create_image(x, y, image=self.dot, anchor=tk.NW, tag='dot')

                    self.locate_apple()

    def move_snake(self):
        """Moves snake"""
        dots = self.find_withtag('dot')
        head = self.find_withtag('head')

        snake = dots + head

        z = 0
        while z < len(snake) - 1:
            c1 = self.coords(snake[z])
            c2 = self.coords(snake[z + 1])
            self.move(snake[z], c2[0] - c1[0], c2[1] - c1[1])
            z += 1

        self.move_s = self.move_x, self.move_y
        self.move(head, self.move_x, self.move_y)

    def game_over(self):
        """Game Over"""
        self.in_game = False

        if self.score > self.high_score:
            self.high_score = self.score
        self.score_board.update_high_score(self.high_score)

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

    def level_up(self):
        """Level up"""
        self.level += 1
        self.score_board.update_level(self.level)
        self.locate_apple()

    def check_level(self):
        """Check for level up"""
        if self.score / self.level > 10:
            self.level_up()

    def replay(self):
        """Replay"""
        self.delete(tk.ALL)
        self.level = 1
        self.score = 0
        self.in_game = True

        # Moves data
        self.move_x = Const.DOT_SIZE
        self.move_y = 0
        # Apple position (will be overwritten)
        self.apple_x = 100
        self.apple_y = 190

        self.init_game()


class ScoreBoard(tk.Canvas):
    """Score Board"""

    def __init__(self):
        """Initialize Score Board"""
        self.score = 0
        self.level = 0
        self.high_score = 0

        super().__init__(width=Const.S_B_W, height=Const.S_B_H,
                         background=Const.S_B_BG)

        self.create_objects()

    def create_objects(self):
        """Creates Objects"""
        self.create_text(10, 10, text=f'Level: {self.level}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='level')
        self.create_text(10, 20, text=f'Score: {self.score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='score')
        self.create_text(10, 30, text=f'High Score: {self.high_score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='h_score')

    def update_level(self, level):
        """Updates level score"""
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
