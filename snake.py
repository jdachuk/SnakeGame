"""
author: edacjos
created: 7/10/19
"""


import json
import random
import os
import numpy as np
from support import Const, Position, Direction, Move
from game_objects import SnakeHead, SnakeTail


class SnakeBrain:
    VERSION = 1.0  # Change version when structure of nodes is changed

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def sigmoid_der(x):
        return SnakeBrain.sigmoid(x) * (1 - SnakeBrain.sigmoid(x))

    def __init__(self):
        self.w_i = 2 * np.random.random((24, 18)) - 1
        self.wh1 = 2 * np.random.random((18, 18)) - 1
        self.w_o = 2 * np.random.random((18,  4)) - 1

        self.learning_rate = .5

    def analyze(self, input_data):
        input_activation = np.dot(input_data, self.w_i)
        input_activation = self.sigmoid(input_activation)

        hidden1_activation = np.dot(input_activation, self.wh1)
        hidden1_activation = self.sigmoid(hidden1_activation)

        output_activation = np.dot(hidden1_activation, self.w_o)
        output_activation = self.sigmoid(output_activation)

        return output_activation

    def train(self, input_data, target_output):
        for _ in range(1000):
            input_value = np.dot(input_data, self.w_i)
            input_activation = self.sigmoid(input_value)

            hidden1_value = np.dot(input_activation, self.wh1)
            hidden1_activation = self.sigmoid(hidden1_value)

            output_value = np.dot(hidden1_activation, self.w_o)
            output_activation = self.sigmoid(output_value)

            mse = ((target_output - output_activation)**2).mean(axis=None)
            print(mse)

            output_errors = (output_activation - target_output) * self.sigmoid_der(output_value)
            delta_w_o = np.dot(hidden1_activation.T, output_errors) * self.learning_rate

            hidden1_errors = np.dot(output_errors, self.w_o.T) * self.sigmoid_der(hidden1_value)
            delta_wh1 = np.dot(input_activation.T, hidden1_errors) * self.learning_rate

            input_errors = np.dot(hidden1_errors, self.wh1.T) * self.sigmoid_der(input_value)
            delta_w_i = np.dot(input_data.T, input_errors) * self.learning_rate

            self.w_o -= delta_w_o
            self.wh1 -= delta_wh1
            self.w_i -= delta_w_i

    def mutate(self):
        for i in range(self.w_i.shape[0]):
            for j in range(self.w_i.shape[1]):
                if random.random() < Const.MUTATION_RATE:
                    mu, sigma = 0, .4
                    mutate_factor = np.random.normal(mu, sigma) / 5
                    self.w_i[i][j] += mutate_factor

        for i in range(self.wh1.shape[0]):
            for j in range(self.wh1.shape[1]):
                if random.random() < Const.MUTATION_RATE:
                    mu, sigma = 0, .4
                    mutate_factor = np.random.normal(mu, sigma) / 5
                    self.wh1[i][j] += mutate_factor

        for i in range(self.w_o.shape[0]):
            for j in range(self.w_o.shape[1]):
                if random.random() < Const.MUTATION_RATE:
                    mu, sigma = 0, .4
                    mutate_factor = np.random.normal(mu, sigma) / 5
                    self.w_o[i][j] += mutate_factor

    def clone(self):
        clone = SnakeBrain()
        clone.w_i = self.w_i
        clone.wh1 = self.wh1
        clone.w_o = self.w_o
        clone.learning_rate = self.learning_rate

        return clone

    def crossover(self, other):
        child = self.clone()

        rand_col = random.randint(0, child.w_i.shape[0])
        rand_row = random.randint(0, child.w_i.shape[1])
        for i in range(child.w_i.shape[0]):
            for j in range(child.w_i.shape[1]):
                if i < rand_col and j < rand_row:
                    child.w_i[i][j] = other.w_i[i][j]

        rand_col = random.randint(0, child.wh1.shape[0])
        rand_row = random.randint(0, child.wh1.shape[1])
        for i in range(child.wh1.shape[0]):
            for j in range(child.wh1.shape[1]):
                if i < rand_col and j < rand_row:
                    child.wh1[i][j] = other.wh1[i][j]

        rand_col = random.randint(0, child.w_o.shape[0])
        rand_row = random.randint(0, child.w_o.shape[1])
        for i in range(child.w_o.shape[0]):
            for j in range(child.w_o.shape[1]):
                if i < rand_col and j < rand_row:
                    child.w_o[i][j] = other.w_o[i][j]

        return child

    def save_to_dict(self):
        w_i = []
        for i in range(self.w_i.shape[0]):
            w_i_r = []
            for j in range(self.w_i.shape[1]):
                w_i_r.append(self.w_i[i][j])
            w_i.append(w_i_r)

        w_h = []
        for i in range(self.wh1.shape[0]):
            w_h_r = []
            for j in range(self.wh1.shape[1]):
                w_h_r.append(self.wh1[i][j])
            w_h.append(w_h_r)

        w_o = []
        for i in range(self.w_o.shape[0]):
            w_o_r = []
            for j in range(self.w_o.shape[1]):
                w_o_r.append(self.w_o[i][j])
            w_o.append(w_o_r)
        result = {
                'version': self.VERSION,
                'weights_input_shape': self.w_i.shape,
                'weights_hidden_shape': self.wh1.shape,
                'weights_output_shape': self.w_o.shape,
                'weights_input': w_i,
                'weights_hidden': w_h,
                'weights_output': w_o
            }
        return result

    def load_from_dict(self, dictionary):
        if int(dictionary['version']) != int(self.VERSION):
            raise ValueError('Inconsistent versions!')
        self.w_i = np.array(dictionary['weights_input'])
        self.wh1 = np.array(dictionary['weights_hidden'])
        self.w_o = np.array(dictionary['weights_output'])


class Snake:

    def __init__(self, game):
        self.game = game
        self.canvas = None

        self.head = SnakeHead(Position(5, 5) * Const.SQUARE_SIZE)
        self.tail = [
            SnakeTail(Position(3, 5) * Const.SQUARE_SIZE),
            SnakeTail(Position(4, 5) * Const.SQUARE_SIZE)
        ]

        self.direction = Direction.EAST
        self.move = self.direction * Const.SQUARE_SIZE

        self.alive = True

    def draw(self, canvas):
        if self.canvas is None:
            self.canvas = canvas
        self.head.draw(self.canvas)
        for tail in self.tail:
            tail.draw(self.canvas)

    def grow(self):
        tail = SnakeTail(self.tail[-1].position)
        tail.draw(self.canvas)
        self.tail.append(tail)

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

                self.grow()

                self.game.locate_apples()

    def check_collisions(self, future_pos):
        """Check collisions with snake tail or borders"""
        for tail in self.tail:
            if tail.position == self.head.position:
                self.alive = False
                self.game.game_over()

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


class SmartSnake(Snake):

    @staticmethod
    def get_label(direction):
        if direction == Direction.NORTH:
            return [0, 0, 0, 1]
        elif direction == Direction.SOUTH:
            return [0, 1, 0, 0]
        elif direction == Direction.EAST:
            return [1, 0, 0, 0]
        elif direction == Direction.WEST:
            return [0, 0, 1, 0]

    def __init__(self, game):
        super().__init__(game)
        self.brain = SnakeBrain()
        self.moves_done = 0
        self.score = 0
        self.bellyful = 300

    def calc_score(self):
        self.score = self.moves_done**(1/2) + len(self.tail) * 3

    def make_decision(self, input_data):
        output = self.brain.analyze(input_data)

        d_idx = 0
        decision = output[0][d_idx]

        for idx, output in enumerate(output[0]):
            if output > decision:
                decision = output
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
            position = position + Move(Const.SQUARE_SIZE, Const.SQUARE_SIZE) * direction
            distance += 1
            item = self.canvas.find_in_position(position + Position(10, 10))
            if len(item) > 0:
                item_tag = self.canvas.gettags(item)
                if 'tail' in item_tag:
                    data[0] = 1 / distance
                    break
                elif 'apple' in item_tag:
                    data[1] = 1 / distance
                    break
        else:
            data[2] = 1 / distance

        return data

    def grow(self):
        self.bellyful += 20
        tail = SnakeTail(self.tail[-1].position)
        tail.draw(self.canvas)
        self.tail.append(tail)

    def make_turn(self):
        self.bellyful -= 1
        if self.bellyful <= 0:
            self.alive = False
            self.game.game_over()

        future_pos = Position(self.head_x, self.head_y) + self.direction * Const.SQUARE_SIZE

        self.check_collisions(future_pos)

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

            self.check_apple_collision(future_pos)

        self.calc_score()

    def train(self, input_data, target_output):
        self.brain.train(input_data, target_output)

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
        version = self.brain.VERSION
        try:
            os.mkdir(os.curdir + '\\data')
        except FileExistsError:
            pass
        try:
            os.mkdir(os.curdir + f'\\data\\V_{version}')
        except FileExistsError:
            pass
        with open(f'data\\V_{version}\\snake_{snake_id}.json', 'w') as json_file:
            data = {
                'generation_id': generation_id,
                'snake_id': snake_id,
                'brain': self.brain.save_to_dict()
            }
            json.dump(data, json_file)

    def load_from_file(self, snake_id):
        version = self.brain.VERSION
        with open(f'data\\V_{version}\\snake_{snake_id}.json', 'r') as json_file:
            try:
                data = json.load(json_file)
                self.brain.load_from_dict(data['brain'])
                return data['generation_id']
            except json.JSONDecodeError:
                return 0
