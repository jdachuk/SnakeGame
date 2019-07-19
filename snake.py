"""
author: edacjos
created: 7/10/19
last modified: 07/13/2019
"""


import json
import random
import os
import numpy as np
from support import Const, Position, Direction, Move
from game_objects import SnakeHead, SnakeTail


class SnakeBrain:
    VERSION = Const.VERSION

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def sigmoid_der(x):
        return SnakeBrain.sigmoid(x) * (1 - SnakeBrain.sigmoid(x))

    def __init__(self):
        self.w_i = 2 * np.random.random((25, 18)) - 1
        self.w_h = 2 * np.random.random((19, 18)) - 1
        self.w_o = 2 * np.random.random((19,  4)) - 1

    def analyze(self, input_data):
        input_data = np.append(input_data, np.ones((1, 1)))  # add bias

        input_activation = np.dot(input_data, self.w_i)
        input_activation = self.sigmoid(input_activation)
        input_activation = np.append(input_activation, np.ones((1, 1)))  # add bias

        hidden_activation = np.dot(input_activation, self.w_h)
        hidden_activation = self.sigmoid(hidden_activation)
        hidden_activation = np.append(hidden_activation, np.ones((1, 1)))  # add bias

        output_activation = np.dot(hidden_activation, self.w_o)
        output_activation = self.sigmoid(output_activation)

        return output_activation

    def mutate(self):
        def weights_mutate(weights):
            for i in range(weights.shape[0]):
                for j in range(weights.shape[1]):
                    if random.random() <= Const.MUTATION_RATE:
                        mutate_factor = np.random.normal(Const.MU, Const.SIGMA)
                        weights[i][j] += mutate_factor / 5

                        if weights[i][j] > 1:
                            weights[i][j] = 1
                        elif weights[i][j] < -1:
                            weights[i][j] = -1

            return weights

        self.w_i = weights_mutate(self.w_i)
        self.w_h = weights_mutate(self.w_h)
        self.w_o = weights_mutate(self.w_o)

    def clone(self):
        clone = SnakeBrain()
        clone.w_i = self.w_i
        clone.w_h = self.w_h
        clone.w_o = self.w_o

        return clone

    def crossover(self, other):

        def weights_crossover(weights, other_w):
            child_w = np.random.random(weights.shape)

            rand_row = random.randint(0, child_w.shape[0])
            rand_col = random.randint(0, child_w.shape[1])

            for i in range(child_w.shape[0]):
                for j in range(child_w.shape[1]):
                    if i < rand_row or (i == rand_row and j <= rand_col):
                        child_w[i][j] = weights[i][j]
                    else:
                        child_w[i][j] = other_w[i][j]

            return child_w

        child = SnakeBrain()

        if random.random() <= Const.CROSSOVER_RATE:
            child.w_i = weights_crossover(self.w_i, other.w_i)
            child.w_h = weights_crossover(self.w_h, other.w_h)
            child.w_o = weights_crossover(self.w_o, other.w_o)

        return child

    def save_to_dict(self):
        def to_py_arr(ndarray):
            array = []
            for i in range(ndarray.shape[0]):
                row = []
                for j in range(ndarray.shape[1]):
                    row.append(ndarray[i][j])
                array.append(row)
            return array

        result = {
            'version': self.VERSION,
            'weights_input_shape': self.w_i.shape,
            'weights_hidden_shape': self.w_h.shape,
            'weights_output_shape': self.w_o.shape,
            'weights_input': to_py_arr(self.w_i),
            'weights_hidden': to_py_arr(self.w_h),
            'weights_output': to_py_arr(self.w_o)
        }
        return result

    def load_from_dict(self, dictionary):
        if int(dictionary['version']) != int(self.VERSION):
            raise ValueError('Inconsistent versions!')
        self.w_i = np.array(dictionary['weights_input'])
        self.w_h = np.array(dictionary['weights_hidden'])
        self.w_o = np.array(dictionary['weights_output'])


class Snake:

    def __init__(self, game):
        self.game = game
        self.canvas = None

        self.head = SnakeHead(Position(15, 15) * Const.SQUARE_SIZE)
        self.tail = [
            SnakeTail(Position(16, 16) * Const.SQUARE_SIZE),
            SnakeTail(Position(16, 15) * Const.SQUARE_SIZE)
        ]
        self.direction = Direction.WEST
        self.move = self.direction * Const.SQUARE_SIZE

        self.alive = True

    def draw(self, canvas):
        if self.canvas is None:
            self.canvas = canvas
        self.head.draw(self.canvas)
        for tail in self.tail:
            tail.draw(self.canvas)

    def die(self):
        self.alive = False
        self.game.game_over()

    def grow(self):
        tail = SnakeTail(self.tail[-1].position)
        tail.draw(self.canvas)
        self.tail.append(tail)

    def make_turn(self):
        self.check_collisions()

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

        self.check_apple_collision()

    def check_apple_collision(self):

        for apple in self.game.apples:
            if apple.position == self.head.position:
                self.game.update_score()
                self.game.delete_apple(apple)

                self.grow()

                self.game.locate_apples()

    def check_collisions(self):
        """Check collisions with snake tail or borders"""
        for tail in self.tail:
            if tail.position == self.head.position:
                self.die()

        future_pos = Position(self.head_x + self.direction.move_x * Const.SQUARE_SIZE,
                              self.head_y + self.direction.move_y * Const.SQUARE_SIZE)

        if future_pos.x < 0 or future_pos.x > Const.G_B_W - Const.SQUARE_SIZE or \
                future_pos.y < 0 or future_pos.y > Const.G_B_H - Const.SQUARE_SIZE:
            self.die()

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


class SmartSnake(Snake):

    def __init__(self, game):
        super().__init__(game)
        self.brain = SnakeBrain()
        self.moves_done = 0
        self.fitness = 0
        self.left_to_live = 150

    def calc_score(self):
        self.fitness = int(self.moves_done**2 * pow(2, len(self.tail)))

    def make_decision(self, input_data):
        output = self.brain.analyze(input_data)

        d_idx = 0
        decision = output[d_idx]

        for idx, out in enumerate(output):
            if out > decision:
                decision = out
                d_idx = idx

        return Const.DIRECTION_KEYS[d_idx]

    def look(self):
        data = np.ndarray((0, 0))

        for direction in Const.DIRECTIONS:
            data = np.append(data, self.look_in_direction(direction))

        return np.array([data])

    def look_in_direction(self, direction):
        data = np.zeros((3, 1))
        position = Position(self.head_x, self.head_y)

        distance = 0

        while 0 < position.x < Const.G_B_W and 0 < position.y < Const.G_B_H:
            distance += 1
            position = position + Move(Const.SQUARE_SIZE, Const.SQUARE_SIZE) * direction
            item = self.canvas.find_in_position(position + Const.SQUARE_SIZE // 2)
            if len(item) > 0:
                item_tag = self.canvas.gettags(item)
                if 'apple' in item_tag:
                    data[0] = 1 / distance
                    break
                elif 'tail' in item_tag:
                    data[1] = 1 / distance
                    break
        else:
            data[2] = 1 / distance

        return data

    def grow(self):
        self.left_to_live += 60
        tail = SnakeTail(self.tail[-1].position)
        tail.draw(self.canvas)
        self.tail.append(tail)

    def make_turn(self):
        self.left_to_live -= 1
        if self.left_to_live < 0:
            self.die()

        self.check_collisions()

        if self.alive:
            self.moves_done += 1
            data = self.look()
            decision = self.make_decision(data)
            self.change_direction(decision)

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

            self.check_apple_collision()

        self.calc_score()

    def clone(self):
        clone = SmartSnake(self.game)
        clone.brain = self.brain.clone()
        return clone

    def mutate(self):
        self.brain.mutate()

    def crossover(self, other):
        child = SmartSnake(self.game)
        child.brain = self.brain.crossover(other.brain)
        return child

    def save_to_file(self, generation_id, snake_id):
        try:
            os.mkdir(os.curdir + '\\data')
        except FileExistsError:
            pass
        try:
            os.mkdir(os.curdir + f'\\data\\V_{Const.VERSION}')
        except FileExistsError:
            pass
        with open(f'data\\V_{Const.VERSION}\\snake_{snake_id}.json', 'w') as json_file:
            data = {
                'generation_id': generation_id,
                'snake_id': snake_id,
                'brain': self.brain.save_to_dict()
            }
            json.dump(data, json_file)

    def load_from_file(self, snake_id):
        with open(f'data\\V_{Const.VERSION}\\snake_{snake_id}.json', 'r') as json_file:
            try:
                data = json.load(json_file)
                self.brain.load_from_dict(data['brain'])
                return data['generation_id']
            except json.JSONDecodeError:
                return 0
