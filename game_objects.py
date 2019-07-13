"""
author: edacjos
created: 7/10/19
"""

import random
from tkinter import NW
from PIL import Image, ImageTk
from support import Const, Position


class GameObject:

    def __init__(self, name, position):
        self.canvas = None
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
            self.id = -1


class SnakeHead(GameObject):

    def __init__(self, position):
        super().__init__('head', position)
        self.image = ImageTk.PhotoImage(Image.open('images/head.png'))


class SnakeTail(GameObject):

    def __init__(self, position):
        super().__init__('tail', position)
        self.image = ImageTk.PhotoImage(Image.open('images/tail.png'))


class Food(GameObject):
    def __init__(self, name):
        rx = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
        ry = random.randint(Const.MIN_RAND_POS, Const.MAX_RAND_POS) * Const.SQUARE_SIZE
        super().__init__(name, Position(rx, ry))


class Apple(Food):

    def __init__(self):
        super().__init__('apple')
        self.image = ImageTk.PhotoImage(Image.open('images/apple.png'))
