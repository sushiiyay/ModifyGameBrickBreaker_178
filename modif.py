
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


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 105
        self.height = 15
        self.ball = None

        item = canvas.create_rectangle(
            x-52, y-7,
            x+52, y+7,
            fill="#FFB6C9",
            outline="#E58BAF",
            width=2,
            tags="paddle"
        )

        super().__init__(canvas, item)

        self.decoration = canvas.create_text(
            x, y,
            text="♡  MEOW  ♡",
            font=("Arial", 9, "bold"),
            fill="#FFFFFF"
        )

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)
            self.canvas.move(self.decoration, offset, 0)

            if self.ball and not self.ball.active:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {
        1: "#FFB6C9",
        2: "#C9B3ED",
        3: "#A9DCCF"
    }

    def __init__(self, canvas, x, y, hits):
        self.width = 65
        self.height = 21
        self.hits = hits

        color = self.COLORS[hits]

        item = canvas.create_rectangle(
            x-32, y-10,
            x+32, y+10,
            fill=color,
            outline="#FFFFFF",
            width=2,
            tags="brick"
        )

        super().__init__(canvas, item)

        self.decoration = canvas.create_text(
            x, y,
            text="♡",
            font=("Arial", 11, "bold"),
            fill="#FFFFFF"
        )

    def hit(self):
        self.hits -= 1

        if self.hits <= 0:
            self.canvas.delete(self.decoration)
            self.delete()
        else:
            self.canvas.itemconfig(
                self.item,
                fill=self.COLORS[self.hits]
            )


def create_sparkles(canvas, x, y):
    symbols = ["♡", "✦", "✧", "♥"]

    for i in range(4):
        dx = random.randint(-15, 15)
        dy = random.randint(-15, 15)

        particle = canvas.create_text(
            x+dx,
            y+dy,
            text=random.choice(symbols),
            fill=random.choice([
                "#FF91B8",
                "#C9A7EB",
                "#F5C6A5"
            ]),
            font=("Arial", 12)
        )

        canvas.after(
            250,
            lambda p=particle: canvas.delete(p)
        )


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG)

        self.lives = 3
        self.score = 0
        self.running = False
        self.game_over = False

        self.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack()

        self.draw_background()

        self.items = {}
        self.ball = None

        self.paddle = Paddle(
            self.canvas,
            WIDTH/2,
            445
        )

        self.create_bricks()

        self.hud_score = self.canvas.create_text(
            90, 25,
            text="SCORE: 0",
            font=("Arial", 13, "bold"),
            fill=DARK
        )

        self.hud_lives = self.canvas.create_text(
            515, 25,
            text="LIVES: ♥ ♥ ♥",
            font=("Arial", 13, "bold"),
            fill="#E58BAF"
        )

        self.add_ball()
        self.show_start_screen()

        self.canvas.focus_set()

        self.canvas.bind(
            "<Left>",
            lambda e: self.paddle.move(-25)
        )

        self.canvas.bind(
            "<Right>",
            lambda e: self.paddle.move(25)
        )

        self.canvas.bind(
            "<space>",
            lambda e: self.start_game()
        )

        self.canvas.bind(
            "r",
            lambda e: self.restart()
        )

        self.canvas.bind(
            "R",
            lambda e: self.restart()
        )

    def draw_background(self):
        self.canvas.create_text(
            WIDTH/2, 475,
            text="♡ CUTE KITTY BRICK BREAKER ♡",
            font=("Arial", 10, "bold"),
            fill="#D49AB4"
        )

        for i in range(15):
            x = random.randint(15, WIDTH-15)
            y = random.randint(45, 410)

            self.canvas.create_text(
                x, y,
                text=random.choice(["✧", "♡", "·"]),
                fill="#F4D3E2",
                font=("Arial", 13)
            )

    def create_bricks(self):
        colors = [1, 2, 3]

        for row in range(4):
            for col in range(8):
                x = 65 + col * 69
                y = 85 + row * 28

                hits = colors[row % 3]

                brick = Brick(
                    self.canvas,
                    x,
                    y,
                    hits
                )

                self.items[brick.item] = brick

    def add_ball(self):
        if self.ball:
            self.ball.delete()

        coords = self.paddle.get_position()
        x = (coords[0] + coords[2]) / 2

        self.ball = Ball(
            self.canvas,
            x,
            415
        )

        self.paddle.ball = self.ball

    def show_start_screen(self):
        self.overlay = self.canvas.create_rectangle(
            100, 170, 510, 325,
            fill="#FFFFFF",
            outline="#F3BDD2",
            width=3
        )

        self.title_text = self.canvas.create_text(
            305, 205,
            text="♡ CUTE KITTY GAME ♡",
            font=("Arial", 23, "bold"),
            fill="#E58BAF"
        )

        self.info_text = self.canvas.create_text(
            305, 260,
            text="Press SPACE to start!",
            font=("Arial", 13),
            fill="#75516B"
        )

    def remove_start_screen(self):
        for item in [
            self.overlay,
            self.title_text,
            self.info_text
        ]:
            self.canvas.delete(item)

    def start_game(self):
        if self.running or self.game_over:
            return

        self.running = True
        self.ball.active = True

        self.remove_start_screen()
        self.game_loop()

    def update_hud(self):
        self.canvas.itemconfig(
            self.hud_score,
            text=f"SCORE: {self.score}"
        )

        self.canvas.itemconfig(
            self.hud_lives,
            text="LIVES: " + "♥ " * self.lives
        )

    def check_collisions(self):
        coords = self.ball.get_position()

        overlapping = self.canvas.find_overlapping(
            *coords
        )

        objects = [
            self.items[item]
            for item in overlapping
            if item in self.items
        ]

        before = len(self.canvas.find_withtag("brick"))

        self.ball.collide(objects)

        after = len(self.canvas.find_withtag("brick"))

        if after < before:
            self.score += 10
            self.update_hud()

    def game_loop(self):
        if not self.running:
            return

        self.check_collisions()

        if len(self.canvas.find_withtag("brick")) == 0:
            self.end_game(
                "YOU WIN! ♡",
                "All bricks are gone! Amazing!"
            )
            return

        if self.ball.get_position()[3] >= HEIGHT:
            self.lives -= 1
            self.update_hud()

            if self.lives <= 0:
                self.end_game(
                    "GAME OVER :(",
                    "Don't give up, kitty!"
                )
                return

            self.running = False
            self.add_ball()

            self.canvas.create_text(
                WIDTH/2, 230,
                text="Oops! Try again ♡",
                font=("Arial", 18, "bold"),
                fill="#E58BAF",
                tags="message"
            )

            self.canvas.after(
                900,
                self.resume_after_life
            )
            return

        self.ball.update()

        self.after(16, self.game_loop)

    def resume_after_life(self):
        self.canvas.delete("message")

        if not self.game_over:
            self.start_game()

    def end_game(self, title, message):
        self.running = False
        self.game_over = True

        self.canvas.create_rectangle(
            95, 175, 515, 320,
            fill="#FFFFFF",
            outline="#E9B8D0",
            width=3
        )

        self.canvas.create_text(
            WIDTH/2, 215,
            text=title,
            font=("Arial", 24, "bold"),
            fill="#E58BAF"
        )

        self.canvas.create_text(
            WIDTH/2, 255,
            text=message,
            font=("Arial", 12),
            fill=DARK
        )

        self.canvas.create_text(
            WIDTH/2, 290,
            text="Press R to play again ♡",
            font=("Arial", 12, "bold"),
            fill="#B28CBF"
        )

    def restart(self):
        self.running = False
        self.game_over = False
        self.score = 0
        self.lives = 3

        self.canvas.delete("all")
        self.items.clear()

        self.draw_background()

        self.paddle = Paddle(
            self.canvas,
            WIDTH/2,
            445
        )

        self.create_bricks()

        self.hud_score = self.canvas.create_text(
            90, 25,
            text="SCORE: 0",
            font=("Arial", 13, "bold"),
            fill=DARK
        )

        self.hud_lives = self.canvas.create_text(
            515, 25,
            text="LIVES: ♥ ♥ ♥",
            font=("Arial", 13, "bold"),
            fill="#E58BAF"
        )

        self.add_ball()
        self.show_start_screen()


if __name__ == "__main__":
    game = Game(root)
    root.mainloop()
