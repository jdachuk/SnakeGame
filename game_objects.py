"""
author: edacjos
created: 7/10/19
last modified: 07/13/2019
"""

import random
from tkinter import NW
from PIL import Image, ImageTk
from support import Const, Position


class GameObject:

    def __init__(self, name, position, canvas=None):
        self.canvas = canvas
        self.name = name
        self.position = position
        self.image = None
        self.id = -1

    def draw(self, canvas):
        self.canvas = canvas
        self.id = self.canvas.create_image(self.position.x, self.position.y,
                                           image=self.image, anchor=NW, tag=self.name)

    def move(self, move):
        if self.id != -1:
            self.canvas.move(self.id, move.move_x, move.move_y)
            self.position = self.position + move

    def delete(self):
        if self.id != -1:
            self.canvas.delete(self.id)
            self.image = None
            self.id = -1


class SnakeHead(GameObject):

    def __init__(self, position):
        super().__init__('head', position)

    def draw(self, canvas):
        self.image = ImageTk.PhotoImage(Image.open('images/head.png'))
        super().draw(canvas)


class SnakeTail(GameObject):

    def __init__(self, position):
        super().__init__('tail', position)

    def draw(self, canvas):
        self.image = ImageTk.PhotoImage(Image.open('images/tail.png'))
        super().draw(canvas)


class Food(GameObject):
    def __init__(self, name, canvas):
        rx = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
        ry = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
        position = Position(rx, ry)
        while len(canvas.find_in_position(position + 10)) > 0:
            rx = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
            ry = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
            position = Position(rx, ry)
        super().__init__(name, position, canvas)

    def draw(self, canvas=None):
        if canvas is None:
            self.id = self.canvas.create_image(self.position.x, self.position.y,
                                               image=self.image, anchor=NW, tag=self.name)
        else:
            self.id = canvas.create_image(self.position.x, self.position.y,
                                          image=self.image, anchor=NW, tag=self.name)


class Apple(Food):

    def __init__(self, canvas):
        super().__init__('apple', canvas)
        self.image = ImageTk.PhotoImage(Image.open('images/apple.png'))
