import tkinter as tk

class Arkanoid:
    def __init__(self, root):
        self.root = root
        self.root.title("Arkanoid PC 2026")
        self.root.resizable(False, False)

        # Ustawienia gry
        self.width = 600
        self.height = 400
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#222")
        self.canvas.pack()

        # Elementy gry
        self.paddle = self.canvas.create_rectangle(250, 370, 350, 385, fill="#00FF00")
        self.ball = self.canvas.create_oval(290, 190, 310, 210, fill="white")
        
        self.ball_speed_x = 3
        self.ball_speed_y = -3
        self.game_running = False
        
        # Tworzenie bloków (Skórka/Konfiguracja)
        self.blocks = []
        self.setup_blocks()

        # Interakcja
        self.canvas.bind("<Motion>", self.move_paddle) # Myszka
        self.root.bind("<space>", self.start_game)      # Klawiatura

        # Komunikat startowy
        self.text_id = self.canvas.create_text(300, 250, text="NACIŚNIJ SPACJĘ", fill="white", font=("Arial", 20))

    def setup_blocks(self):
        colors = ["#ff4444", "#ffbb33", "#00C851", "#33b5e5"]
        for row in range(4):
            for col in range(10):
                x1 = col * 60 + 2
                y1 = row * 25 + 30
                x2 = x1 + 56
                y2 = y1 + 20
                block = self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[row], outline="black")
                self.blocks.append(block)

    def move_paddle(self, event):
        x = event.x
        self.canvas.coords(self.paddle, x-50, 370, x+50, 385)

    def start_game(self, event=None):
        if not self.game_running:
            self.game_running = True
            self.canvas.delete(self.text_id)
            self.update()

    def update(self):
        if not self.game_running: return

        # Ruch piłki
        self.canvas.move(self.ball, self.ball_speed_x, self.ball_speed_y)
        pos = self.canvas.coords(self.ball)

        # Odbicia od ścian
        if pos[0] <= 0 or pos[2] >= self.width:
            self.ball_speed_x *= -1
        if pos[1] <= 0:
            self.ball_speed_y *= -1
        
        # Kolizja z paletką
        paddle_pos = self.canvas.coords(self.paddle)
        if pos[3] >= paddle_pos[1] and pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
            self.ball_speed_y = -abs(self.ball_speed_y)

        # Kolizja z blokami
        items = self.canvas.find_overlapping(*pos)
        for item in items:
            if item in self.blocks:
                self.canvas.delete(item)
                self.blocks.remove(item)
                self.ball_speed_y *= -1
                break

        # Przegrana
        if pos[3] >= self.height:
            self.game_over()
            return

        # Wygrana
        if not self.blocks:
            self.victory()
            return

        self.root.after(10, self.update)

    def game_over(self):
        self.game_running = False
        self.text_id = self.canvas.create_text(300, 200, text="KONIEC GRY", fill="red", font=("Arial", 30))

    def victory(self):
        self.game_running = False
        self.text_id = self.canvas.create_text(300, 200, text="WYGRANA!", fill="gold", font=("Arial", 30))

if __name__ == "__main__":
    root = tk.Tk()
    Arkanoid(root)
    root.mainloop()