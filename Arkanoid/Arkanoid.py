import tkinter as tk

class Arkanoid:
    def __init__(self, root):
        self.root = root
        self.root.title("Arkanoid PC 2026 - Smooth Keyboard Edition")
        self.root.resizable(False, False)

        # Konfiguracja skórek
        self.skins = {
            "Neon": {"bg": "#000", "paddle": "#00FFFF", "ball": "#FF00FF", "text": "#00FFFF"},
            "Retro": {"bg": "#222", "paddle": "#00FF00", "ball": "white", "text": "white"},
            "Classic": {"bg": "#003366", "paddle": "#FFD700", "ball": "#FFFFFF", "text": "#FFD700"}
        }
        self.current_skin = "Retro"

        self.skin_frame = tk.Frame(root)
        self.skin_frame.pack(fill="x")
        for skin_name in self.skins.keys():
            btn = tk.Button(self.skin_frame, text=skin_name, command=lambda s=skin_name: self.change_skin(s))
            btn.pack(side="left", expand=True, fill="x")

        self.width = 600
        self.height = 400
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg=self.skins[self.current_skin]["bg"],
                                highlightthickness=0)
        self.canvas.pack()

        # Stan gry
        self.game_running = False
        self.game_ended = False
        self.blocks = []
        
        # --- LOGIKA PŁYNNEGO RUCHU ---
        self.keys_pressed = {"Left": False, "Right": False}
        self.paddle_speed = 7 # Prędkość na klatkę (płynny ruch)

        self.init_game_objects()

        # Powiązania klawiszy (naciśnięcie i puszczenie)
        self.root.bind("<KeyPress-Left>", lambda e: self.set_key("Left", True))
        self.root.bind("<KeyRelease-Left>", lambda e: self.set_key("Left", False))
        self.root.bind("<KeyPress-Right>", lambda e: self.set_key("Right", True))
        self.root.bind("<KeyRelease-Right>", lambda e: self.set_key("Right", False))
        self.root.bind("<space>", self.handle_space)

    def set_key(self, key, state):
        self.keys_pressed[key] = state

    def init_game_objects(self):
        self.canvas.delete("all")
        skin = self.skins[self.current_skin]
        self.paddle = self.canvas.create_rectangle(250, 370, 350, 385, fill=skin["paddle"], outline="white")
        self.ball = self.canvas.create_oval(290, 190, 310, 210, fill=skin["ball"], outline="white")
        self.ball_speed_x = 4
        self.ball_speed_y = -4
        self.setup_blocks()
        self.text_id = self.canvas.create_text(300, 250, text="PRZYTRZYMAJ STRZAŁKI I NACIŚNIJ SPACJĘ",
                                               fill=skin["text"], font=("Arial", 12, "bold"))

    def setup_blocks(self):
        colors = ["#ff4444", "#ffbb33", "#00C851", "#33b5e5"]
        for row in range(4):
            for col in range(10):
                x1, y1 = col * 60 + 2, row * 25 + 30
                x2, y2 = x1 + 56, y1 + 20
                block = self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[row], outline="black")
                self.blocks.append(block)

    def change_skin(self, skin_name):
        if not self.game_running:
            self.current_skin = skin_name
            self.canvas.config(bg=self.skins[skin_name]["bg"])
            self.init_game_objects()

    def update_paddle(self):
        """Przemieszcza paletkę na podstawie wciśniętych klawiszy"""
        if not self.game_ended:
            dx = 0
            if self.keys_pressed["Left"]: dx -= self.paddle_speed
            if self.keys_pressed["Right"]: dx += self.paddle_speed
            
            pos = self.canvas.coords(self.paddle)
            if pos[0] + dx >= 0 and pos[2] + dx <= self.width:
                self.canvas.move(self.paddle, dx, 0)

    def handle_space(self, event):
        if self.game_ended:
            self.game_ended = False
            self.init_game_objects()
        elif not self.game_running:
            self.game_running = True
            self.canvas.delete(self.text_id)
            self.update()

    def update(self):
        if not self.game_running or self.game_ended: return

        # Najpierw rusz paletką (sprawdzanie klawiszy)
        self.update_paddle()

        # Potem rusz piłką i sprawdź kolizje
        self.canvas.move(self.ball, self.ball_speed_x, self.ball_speed_y)
        pos = self.canvas.coords(self.ball)

        if pos[0] <= 0 or pos[2] >= self.width:
            self.ball_speed_x *= -1
        if pos[1] <= 0:
            self.ball_speed_y *= -1

        paddle_pos = self.canvas.coords(self.paddle)
        if pos[3] >= paddle_pos[1] and pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
            if self.ball_speed_y > 0:
                self.ball_speed_y *= -1

        items = self.canvas.find_overlapping(*pos)
        for item in items:
            if item in self.blocks:
                self.canvas.delete(item)
                self.blocks.remove(item)
                self.ball_speed_y *= -1
                break

        if pos[3] >= self.height:
            self.end_game("KONIEC GRY", "red")
        elif not self.blocks:
            self.end_game("WYGRANA!", "gold")
        else:
            self.root.after(10, self.update)

    def end_game(self, message, color):
        self.game_running = False
        self.game_ended = True
        self.canvas.create_text(300, 200, text=message, fill=color, font=("Arial", 30, "bold"))
        self.canvas.create_text(300, 240, text="Spacja, aby spróbować ponownie", fill="white", font=("Arial", 12))

if __name__ == "__main__":
    root = tk.Tk()
    Arkanoid(root)
    root.mainloop()
