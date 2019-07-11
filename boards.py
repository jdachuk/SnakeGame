"""
author: edacjos
created: 7/10/19
"""

import tkinter as tk
from support import Const


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
        self.create_text(10, 30, text=f'Score: {self.score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='score')
        self.create_text(10, 50, text=f'High Score: {self.high_score}', font=Const.S_F,
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


class StatisticBoardAI(StatisticBoard):
    def __init__(self, snakes_total):
        self.generation_id = 0
        self.snake_id = 0
        self.snakes_total = snakes_total

        super().__init__()

    def create_objects(self):
        if self.display_level:
            self.create_text(10, 10, text=f'Level: {self.level}', font=Const.S_F,
                             fill='white', anchor=tk.W, tag='level')
        self.create_text(10, 30, text=f'Score: {self.score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='score')
        self.create_text(10, 50, text=f'High Score: {self.high_score}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='h_score')
        self.create_text(10, 70, text=f'Generation: {self.generation_id}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='population')
        self.create_text(10, 90, text=f'Snake: {self.snake_id}/{self.snakes_total}', font=Const.S_F,
                         fill='white', anchor=tk.W, tag='snake')

    def update_population(self, population_id):
        self.generation_id = population_id
        self.itemconfigure('population', text=f'Generation: {self.generation_id}')

    def update_snake(self, snake_id):
        self.snake_id = snake_id
        self.itemconfigure('snake', text=f'Snake: {self.snake_id}/{self.snakes_total}')

    def update_info_(self, level, score, h_score, population_id, snake_id):
        super().update_info(level, score, h_score)
        self.update_population(population_id)
        self.update_snake(snake_id)
