"""
author: Josyp Dachuk
created: 07/06/2019
last modified: 07/13/2019
"""

import tkinter as tk
from boards import GameBoard, StatisticBoard, StatisticBoardAI
from snake import Snake
from population import Population
from support import Const
from game_objects import Apple


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

        self.statistic_board = None
        self.board = GameBoard()

        self.level = 1
        self.score = 0
        self.high_score = 0

        self.apples = []
        self.snake = Snake(self)

        self.paused = False
        self.in_game = True
        self.level_system = True

        self.bind_all('<Key>', self.on_key_pressed)
        self.after_id = None

    def init_game(self):
        """Initialize game objects and starts game"""
        self.snake.draw(self.board)
        self.locate_apples()
        self.statistic_board = StatisticBoard()
        self.statistic_board.grid(column=0, row=0)
        self.board.grid(column=1, row=0)
        self.statistic_board.update_info(self.level, self.score, self.high_score)

        self.after_id = self.after(Const.DELAY, self.on_timer)

    def locate_apples(self):
        """Locating an apple"""
        while len(self.apples) < self.level:
            apple = Apple(self.board)
            apple.draw()
            self.apples.append(apple)

    def on_timer(self):
        """On timer tick function"""
        if not self.paused and self.in_game:
            self.snake.make_turn()
            self.check_level_up()

            delay = Const.DELAY - (self.level - 1) * Const.SPEED_INCREASE
            if delay >= Const.MIN_DELAY:
                self.after_id = self.after(delay, self.on_timer)
            else:
                self.after_id = self.after(Const.MIN_DELAY, self.on_timer)

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

        self.snake = Snake(self)
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
        self.after_cancel(self.after_id)

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


class SnakeGameAI(SnakeGame):

    def __init__(self):
        super().__init__()
        self.population = Population(self)

        self.delay = Const.MIN_DELAY
        self.statistic_board = StatisticBoardAI(self.population.size)
        self.statistic_board.grid(column=0, row=0)
        self.board.grid(column=1, row=0)

    def init_game(self):
        """Initialize game objects and starts game"""
        self.snake = self.population.get_snake()
        self.snake.draw(self.board)

        self.locate_apples()

        self.statistic_board.update_info_(self.level, self.score, self.high_score,
                                          self.population.generation_id, self.population.snake_in_game_id)

        self.after_id = self.after(self.delay, self.on_timer)

    def on_timer(self):
        """On timer tick function"""
        if not self.paused and self.in_game:
            self.snake.make_turn()
            self.check_level_up()

            self.after_id = self.after(self.delay, self.on_timer)

    def on_key_pressed(self, event):
        """Key pressed listener"""
        key = event.keysym

        # Pause
        if key == self.ControlKeys.SPACE_KEY:
            if not self.paused:
                self.pause()
            else:
                self.unpause()
        elif key == Const.RIGHT_KEY:
            self.speed_up()
        elif key == Const.LEFT_KEY:
            self.slow_down()

    def speed_up(self):
        self.delay = self.delay // 2

    def slow_down(self):
        self.delay = self.delay * 2

    def replay(self):
        """Replay"""
        self.board.delete(tk.ALL)
        self.level = 1
        self.score = 0
        self.in_game = True

        self.snake = self.population.next_snake()
        self.statistic_board.update_snake(self.population.snake_in_game_id)
        self.statistic_board.update_population(self.population.generation_id)
        self.apples = []

        self.init_game()

    def game_over(self):
        """Game Over"""
        self.in_game = False

        if self.score > self.high_score:
            self.high_score = self.score
            self.statistic_board.update_high_score(self.high_score)

        self.after_cancel(self.after_id)
        self.replay()


def start_snake():
    root = tk.Tk()
    game = SnakeGame()
    game.init_game()
    root.mainloop()


def start_snake_ai():
    root = tk.Tk()
    game = SnakeGameAI()
    game.init_game()
    root.mainloop()


if __name__ == '__main__':
    start_snake_ai()
