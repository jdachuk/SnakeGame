"""
author: edacjos
created: 7/10/19
"""

import random
import threading
from snake import SmartSnake


class Population:
    def __init__(self, game, canvas):
        self.snakes = []
        self.game = game
        self.canvas = canvas
        self.size = 1000
        self.snake_in_game_id = 0
        self.generation_id = 0
        self.done = False

        chose = input('Load last generation?[y/n] ')
        if chose.lower() == 'y':
            self.load_last_generation()
        else:
            self.create_snakes()

    def create_snakes(self):
        for _ in range(self.size):
            snake = SmartSnake(self.game, self.canvas)
            self.snakes.append(snake)

    def train_snakes(self, input_data, target_output):
        for snake in self.snakes:
            snake.train(input_data, target_output)

    def sort_snakes_by_score(self):
        self.snakes.sort(key=lambda snake: snake.score)

    def select_best(self, n=None):
        if n is None:
            n = len(self.snakes) // 2
        mean_score = 0
        for snake in self.snakes:
            mean_score += snake.score
        mean_score /= len(self.snakes)
        result = []
        for snake in self.snakes:
            if snake.score >= mean_score:
                result.append(snake.clone())
            if len(result) >= n:
                break
        return result

    @staticmethod
    def select_snake(snakes):
        max_score = 0
        mean_score = 0

        for snake in snakes:
            mean_score += snake.score
            if snake.score > max_score:
                max_score = snake.score

        mean_score /= len(snakes)

        rand = random.randint(mean_score, max_score)

        for snake in snakes:
            if snake.score >= rand:
                return snake

    def natural_selection(self):
        new_generation = self.select_best()
        kids = []

        while len(new_generation) + len(kids) < self.size:
            parent1 = self.select_snake(new_generation)
            parent2 = self.select_snake(new_generation)

            child = parent1.crossover(parent2)

            child.mutate()

            kids.append(child)

        self.snakes = new_generation + kids

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

    def load_last_generation(self):
        self.snakes = []
        try:
            for idx in range(self.size):
                snake = SmartSnake(self.game, self.canvas)
                self.generation_id = snake.load_from_file(idx)
                self.snakes.append(snake)
        except FileNotFoundError:
            answer = input('Can\'t load last population! Generate snakes randomly? [y/n]')

            if answer.lower() == 'y':
                self.snakes = []
                self.create_snakes()
            else:
                raise Exception('Not full population!')
