"""
author: edacjos
created: 7/10/19
last modified: 07/13/2019
"""

import random
import threading
from snake import SmartSnake
from support import Const


class Population:
    def __init__(self, game):
        self.snakes = []
        self.top_snake = None
        self.game = game
        self.size = 1000
        self.snake_in_game_id = 0
        self.generation_id = 0
        self.done = False

        try:
            with open(f'data\\V_{Const.VERSION}\\snake_0.json', 'r'):
                chose = input('Found previous run of this version. Load last generation?[y/n] ')
                if chose.lower() == 'y':
                    self.load_last_generation()
                else:
                    self.create_snakes()
        except FileNotFoundError:
            self.create_snakes()

    def create_snakes(self):
        for _ in range(self.size):
            snake = SmartSnake(self.game)
            self.snakes.append(snake)

    @staticmethod
    def sort_by_score(snakes):
        result = snakes
        result.sort(key=lambda snake: snake.score)
        return result

    def select_best(self, n=None):
        if n is None:
            n = len(self.snakes) // 2

        snakes = self.sort_by_score(self.snakes)

        return snakes[len(snakes) - n:]

    @staticmethod
    def select_snake(snakes):
        rand_idx = random.randint(0, len(snakes) - 1)
        return snakes[rand_idx]

    def select_top_snake(self):
        score = 0
        for snake in self.snakes:
            if snake.score > score:
                score = snake.score
                self.top_snake = snake

    def natural_selection(self):
        self.select_top_snake()
        top_snakes = self.select_best()

        for idx in range(len(top_snakes)):
            top_snakes[idx] = top_snakes[idx].clone()

        kids = []

        rand_snake = self.select_snake(top_snakes)
        child_top = self.top_snake.crossover(rand_snake)
        child_top.mutate()

        kids.append(child_top)

        while len(top_snakes) + len(kids) < self.size:
            parent1 = self.select_snake(top_snakes)
            parent2 = self.select_snake(top_snakes)

            child = parent1.crossover(parent2)

            child.mutate()

            kids.append(child)

        self.snakes = top_snakes + kids

        self.generation_id += 1
        self.done = False
        self.snake_in_game_id = 0
        print(f'New generation {self.generation_id} of snakes')
        threading.Thread(target=self.save).start()

    def get_snake(self):
        return self.snakes[self.snake_in_game_id]

    def next_snake(self):
        self.is_done()
        if self.done:
            self.natural_selection()
        else:
            self.snake_in_game_id += 1
        return self.get_snake()

    def is_done(self):
        done = True
        for snake in self.snakes:
            done = done and not snake.alive

        if done:
            self.done = True

    def save(self):
        for idx, snake in enumerate(self.snakes):
            snake.save_to_file(self.generation_id, idx)
        print(f'Generation {self.generation_id} successfully saved!')

    def load_last_generation(self):
        self.snakes = []
        try:
            for idx in range(self.size):
                snake = SmartSnake(self.game)
                self.generation_id = snake.load_from_file(idx)
                self.snakes.append(snake)
        except FileNotFoundError:
            answer = input('Can\'t load last generation! Generate snakes randomly? [y/n]')

            if answer.lower() == 'y':
                self.snakes = []
                self.create_snakes()
            else:
                raise Exception('Not full population!')
