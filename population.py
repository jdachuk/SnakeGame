"""
author: edacjos
created: 7/10/19
last modified: 07/13/2019
"""

import os
import random
import threading
import json
import csv
from snake import SmartSnake
from support import Const


class Population:
    def __init__(self, game):
        self.snakes = []
        self.top_snake = None
        self.game = game
        self.size = Const.POPULATION_SIZE
        self.snake_in_game_id = 0
        self.generation_id = 0
        self.done = False
        self.total_fitness = 0

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

    def select_snake(self):
        rand = self.total_fitness * random.random()

        cum_sum = 0
        for snake in self.snakes:
            cum_sum += snake.fitness
            if cum_sum >= rand:
                return snake

    def select_top_snake(self):
        max_fitness = 0
        for snake in self.snakes:
            if snake.fitness > max_fitness:
                max_fitness = snake.fitness
                self.top_snake = snake
        threading.Thread(target=self.save_top_snake).start()

    def calculate_total_fitness(self):
        total = 0
        for snake in self.snakes:
            total += snake.fitness
        self.total_fitness = total

    def natural_selection(self):
        self.calculate_total_fitness()
        self.select_top_snake()
        new_generation = [self.top_snake.clone()]

        while len(new_generation) < self.size:
            parent1 = self.select_snake()
            parent2 = self.select_snake()

            child = parent1.crossover(parent2)
            child.mutate()

            new_generation.append(child)

        self.snakes = new_generation

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

    def save_top_snake(self):
        try:
            os.mkdir(os.curdir + '\\data')
        except FileExistsError:
            pass
        try:
            os.mkdir(os.curdir + f'\\data\\V_{Const.VERSION}')
        except FileExistsError:
            pass
        try:
            os.mkdir(os.curdir + f'\\data\\V_{Const.VERSION}\\top_snakes')
        except FileExistsError:
            pass
        try:
            os.mkdir(os.curdir + f'\\data\\V_{Const.VERSION}\\info')
        except FileExistsError:
            pass
        with open(f'data\\V_{Const.VERSION}\\top_snakes\\gen_{self.generation_id}.json', 'w') as json_file:
            data = {
                'generation_id': self.generation_id,
                'generation_size': self.size,
                'total_fitness': self.total_fitness,
                'generation_avg_fitness': self.total_fitness / self.size,
                'snake_fitness': self.top_snake.fitness,
                'snake_brain': self.top_snake.brain.save_to_dict()
            }
            json.dump(data, json_file)
        with open(f'data\\V_{Const.VERSION}\\info\\progress.csv', 'a') as csv_file:
            fieldnames = ['generation_id', 'generation_size', 'total_fitness', 'top_fitness']
            csv_writer = csv.DictWriter(csv_file, fieldnames)
            new_data = {
                'generation_id': self.generation_id,
                'generation_size': self.size,
                'total_fitness': self.total_fitness,
                'top_fitness': self.top_snake.fitness
            }
            csv_writer.writerow(new_data)
