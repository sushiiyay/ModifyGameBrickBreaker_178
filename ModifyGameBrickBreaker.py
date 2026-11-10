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

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 11
        self.direction = [0.65, -1]
        self.speed = 5
        self.active = False

        item = canvas.create_oval(
            x-11, y-11, x+11, y+11,
            fill="#FFCEE0",
            outline="#E58BAF",
            width=2
        )

        super().__init__(canvas, item)

        self.face = canvas.create_text(
            x, y,
            text="🐱",
            font=("Segoe UI Emoji", 15)
        )

    def move(self, x, y):
        super().move(x, y)
        self.canvas.move(self.face, x, y)

    def delete(self):
        self.canvas.delete(self.face)
        super().delete()

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1

        if coords[1] <= 0:
            self.direction[1] *= -1

        self.move(
            self.direction[0] * self.speed,
            self.direction[1] * self.speed
        )

    def collide(self, objects):
        if not objects:
            return

        ball = self.get_position()
        center_x = (ball[0] + ball[2]) / 2
        center_y = (ball[1] + ball[3]) / 2

        for obj in objects:
            coords = obj.get_position()

            if isinstance(obj, Brick):
                obj.hit()
                self.direction[1] *= -1

                create_sparkles(
                    self.canvas,
                    center_x,
                    center_y
                )
                break

            elif isinstance(obj, Paddle):
                self.direction[1] = -abs(self.direction[1])

                paddle_center = (coords[0] + coords[2]) / 2
                offset = (center_x - paddle_center) / 45

                self.direction[0] = max(
                    -1, min(1, offset)
                )

                length = math.sqrt(
                    self.direction[0]**2 +
                    self.direction[1]**2
                )

                self.direction[0] /= length
                self.direction[1] /= length
                break

