import tkinter as tk
import random
import math

WIDTH = 610
HEIGHT = 500

BG = "#FFF0F5"
PINK = "#FFB6C9"
PURPLE = "#DCC6F2"
WHITE = "#FFFFFF"
DARK = "#75516B"

root = tk.Tk()
root.title("♡ Kitty Pop - Cute Brick Breaker ♡")
root.resizable(False, False)
root.configure(bg=BG)

class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)
