"""
author: edacjos
created: 7/10/19
"""

import random
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

    def kill_worst(self, n=None):
        if n is None:
            n = len(self.snakes) // 2
        self.sort_snakes_by_score()
        self.snakes = self.snakes[n:]

    def select_snake(self):
        score_sum = 0
        for snake in self.snakes:
            score_sum += snake.score

        rand = random.randint(0, score_sum)

        selection_sum = 0
        for snake in self.snakes:
            selection_sum += snake.score
            if selection_sum > rand:
                return snake

        return self.snakes[0]

    def natural_selection(self):
        self.kill_worst()

        for i in range(0, len(self.snakes), 2):
            snake1 = self.snakes[i].crossover(self.snakes[i+1])
            snake2 = self.snakes[i+1].crossover(self.snakes[i])

            if random.randint(0, 10) == 0:
                snake1.mutate()
                snake2.mutate()

            self.snakes.insert(0, snake1)
            self.snakes.insert(0, snake2)

        for idx in range(len(self.snakes)):
            self.snakes[idx] = self.snakes[idx].clone()

        self.generation_id += 1
        self.done = False
        self.snake_in_game_id = 0
        print(f'New generation {self.generation_id} of snakes')

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
