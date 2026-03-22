import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import random
import time

class SCADA_System:
    def __init__(self, root):
        self.root = root
        self.root.title("PRO-INDUSTRY SCADA v2.1 - Panel Dyspozytorski")
        self.root.geometry("700x550")
        self.root.configure(bg="#2c3e50")
        
        # Zmienne procesowe
        self.operator = ""
        self.is_running = False
        self.cooling_active = False
        self.line_efficiency = 100
        
        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = tk.Frame(self.root, bg="#34495e", bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=250)

        tk.Label(self.login_frame, text="LOGOWANIE SYSTEMOWE", font=("Segoe UI", 12, "bold"), bg="#34495e", fg="white").pack(pady=15)
        
        tk.Label(self.login_frame, text="ID Operatora:", bg="#34495e", fg="#ecf0f1").pack()
        self.ent_user = tk.Entry(self.login_frame, justify="center")
        self.ent_user.insert(0, "Kszyszkovski")
        self.ent_user.pack(pady=5)

        tk.Label(self.login_frame, text="Hasło:", bg="#34495e", fg="#ecf0f1").pack()
        self.ent_pass = tk.Entry(self.login_frame, show="*", justify="center")
        self.ent_pass.pack(pady=5)

        tk.Button(self.login_frame, text="ZALOGUJ", command=self.handle_login, bg="#27ae60", fg="white", width=15).pack(pady=20)

    def handle_login(self):
        if self.ent_pass.get() == "admin123":
            self.operator = self.ent_user.get()
            self.login_frame.destroy()
            self.setup_main_ui()
            self.start_monitoring()
        else:
            messagebox.showerror("Błąd", "Nieautoryzowany dostęp!")

    def setup_main_ui(self):
        # Panel górny (Status)
        top_bar = tk.Frame(self.root, bg="#1a252f", height=40)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text=f"Operator: {self.operator}", bg="#1a252f", fg="#bdc3c7").pack(side="left", padx=10)
        
        # Dashboard
        self.dash = tk.Frame(self.root, bg="#2c3e50")
        self.dash.pack(fill="both", expand=True, padx=20, pady=20)

        # Wskaźniki
        self.lbl_cpu = tk.Label(self.dash, text="Obciążenie CPU: --%", font=("Consolas", 14), bg="#2c3e50", fg="#ecf0f1")
        self.lbl_cpu.grid(row=0, column=0, pady=10, sticky="w")

        self.lbl_temp = tk.Label(self.dash, text="Temp. Procesu: --°C", font=("Consolas", 14), bg="#2c3e50", fg="#ecf0f1")
        self.lbl_temp.grid(row=1, column=0, pady=10, sticky="w")

        self.lbl_speed = tk.Label(self.dash, text="Wydajność Linii: 100%", font=("Consolas", 14), bg="#2c3e50", fg="#ecf0f1")
        self.lbl_speed.grid(row=2, column=0, pady=10, sticky="w")

        # Status wizualny
        self.status_box = tk.Label(self.dash, text="SYSTEM AKTYWNY", bg="#27ae60", fg="white", font=("Arial", 16, "bold"), width=25)
        self.status_box.grid(row=3, column=0, columnspan=2, pady=20)

        # Logi
        tk.Label(self.dash, text="Dziennik zdarzeń:", bg="#2c3e50", fg="#bdc3c7").grid(row=4, column=0, sticky="w")
        self.log_area = tk.Text(self.dash, height=10, width=70, state="disabled", bg="#1a252f", fg="#2ecc71")
        self.log_area.grid(row=5, column=0, columnspan=2)

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def start_monitoring(self):
        self.is_running = True
        self.run_process_loop()
        self.schedule_autodiagnostics()

    def run_process_loop(self):
        if not self.is_running: return
        
        cpu = psutil.cpu_percent()
        # Symulacja parametrów procesu na podstawie PC
        temp = 40 + (cpu * 0.6) + random.uniform(-2, 2)
        
        self.lbl_cpu.config(text=f"Obciążenie CPU (Moc wejściowa): {cpu}%")
        self.lbl_temp.config(text=f"Temp. Silników: {temp:.1f}°C")
        
        # LOGIKA REAKCJI
        if temp > 75:
            self.status_box.config(text="ALARM: PRZEGRZANIE", bg="#e74c3c")
            self.line_efficiency = 40
            self.log("KRYTYCZNE PRZEGRZANIE! Redukcja prędkości do 40%.")
            self.cooling_active = True
        elif temp > 60:
            self.status_box.config(text="OSTRZEŻENIE: WYSOKA TEMP", bg="#f39c12")
            self.line_efficiency = 75
            self.log("Wysoka temperatura. Włączono chłodzenie pomocnicze.")
        else:
            self.status_box.config(text="PRACA NOMINALNA", bg="#27ae60")
            self.line_efficiency = 100
            if self.cooling_active:
                self.log("Temperatura ustabilizowana. Powrót do 100% mocy.")
                self.cooling_active = False

        self.lbl_speed.config(text=f"Wydajność Linii: {self.line_efficiency}%")
        
        # Losowe awarie (1% szansy na cykl)
        if random.random() < 0.01:
            self.log("AWARIA LOSOWA: Błąd czujnika taśmy nr 2!")
            messagebox.showwarning("AWARIA", "Wykryto błąd mechaniczny! Sprawdź sekcję 2.")

        self.root.after(2000, self.run_process_loop)

    def schedule_autodiagnostics(self):
        # Okresowe sprawdzanie obecności (co 30-50 sekund)
        delay = random.randint(30000, 50000)
        self.root.after(delay, self.presence_check)

    def presence_check(self):
        if not self.is_running: return
        
        self.log("PROCEDURA AUTODIAGNOSTYKI: Oczekiwanie na operatora...")
        
        check_win = tk.Toplevel(self.root)
        check_win.title("WERYFIKACJA")
        check_win.geometry("300x150")
        check_win.attributes("-topmost", True) # Zawsze na wierzchu
        
        tk.Label(check_win, text="POTWIERDŹ OBECNOŚĆ\n(Czas na reakcję: 30s)", font=("Arial", 10, "bold")).pack(pady=20)
        
        status = {"responded": False}

        def on_confirm():
            status["responded"] = True
            check_win.destroy()
            self.log("Autodiagnostyka pomyślna. Operator obecny.")
            self.schedule_autodiagnostics()

        tk.Button(check_win, text="JESTEM OBECNY (F1)", command=on_confirm, bg="#2980b9", fg="white").pack()

        # Timer 30 sekund
        def on_timeout():
            if not status["responded"]:
                check_win.destroy()
                self.is_running = False
                self.log("ALARM! BRAK OPERATORA! SYSTEM ZATRZYMANY.")
                messagebox.showerror("KRYTYCZNY BŁĄD", "Brak potwierdzenia obecności w ciągu 30s.\nNastępuje wylogowanie i zatrzymanie linii!")
                self.main_frame_reset()

        self.root.after(30000, on_timeout)

    def main_frame_reset(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = SCADA_System(root)
    root.mainloop()