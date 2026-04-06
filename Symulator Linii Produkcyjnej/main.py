import tkinter as tk
from tkinter import messagebox, ttk
import psutil
import random
import time

class SCADASystem:
    def __init__(self, root):
        self.root = root
        self.root.title("PRO-INDUSTRY SCADA v3.0 - Panel Dyspozytorski")
        self.root.geometry("850x650")
        self.root.configure(bg="#2c3e50")
        
        # Zmienne procesowe
        self.operator = ""
        self.is_running = False
        self.cooling_active = False
        self.line_efficiency = 100
        self.production_count = 0
        self.belt_position = 0
        
        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = tk.Frame(self.root, bg="#34495e", bd=2, relief="groove")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=250)

        tk.Label(self.login_frame, text="LOGOWANIE SYSTEMOWE", font=("Segoe UI", 12, "bold"), bg="#34495e", fg="white").pack(pady=15)
        
        tk.Label(self.login_frame, text="ID Operatora:", bg="#34495e", fg="#ecf0f1").pack()
        self.ent_user = tk.Entry(self.login_frame, justify="center")
        self.ent_user.insert(0, "admin123")
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
        # --- Panel górny (Status) ---
        top_bar = tk.Frame(self.root, bg="#1a252f", height=40)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text=f"Operator: {self.operator}", bg="#1a252f", fg="#bdc3c7", font=("Arial", 10, "bold")).pack(side="left", padx=10)
        
        self.status_box = tk.Label(top_bar, text="SYSTEM AKTYWNY", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), width=25)
        self.status_box.pack(side="right", padx=10, pady=5)

        # --- Główny kontener ---
        main_content = tk.Frame(self.root, bg="#2c3e50")
        main_content.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Lewy panel: Parametry PC i silników ---
        params_frame = tk.LabelFrame(main_content, text="Parametry Systemu (Diagnostyka)", bg="#34495e", fg="white", font=("Arial", 11, "bold"), padx=10, pady=10)
        params_frame.pack(side="left", fill="y", expand=False, ipadx=20)

        self.lbl_cpu = tk.Label(params_frame, text="Obciążenie CPU: --%", font=("Consolas", 12), bg="#34495e", fg="#ecf0f1")
        self.lbl_cpu.pack(anchor="w", pady=5)

        self.lbl_ram = tk.Label(params_frame, text="Zajętość RAM: --%", font=("Consolas", 12), bg="#34495e", fg="#ecf0f1")
        self.lbl_ram.pack(anchor="w", pady=5)

        self.lbl_temp = tk.Label(params_frame, text="Temp. Napędów: --°C", font=("Consolas", 12, "bold"), bg="#34495e", fg="#e74c3c")
        self.lbl_temp.pack(anchor="w", pady=15)

        self.lbl_fans = tk.Label(params_frame, text="Wentylatory: GŁÓWNE [ON]", font=("Consolas", 12), bg="#34495e", fg="#3498db")
        self.lbl_fans.pack(anchor="w", pady=5)

        # --- Prawy panel: Wizualizacja Produkcji ---
        prod_frame = tk.LabelFrame(main_content, text="Linia Produkcyjna", bg="#34495e", fg="white", font=("Arial", 11, "bold"), padx=10, pady=10)
        prod_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

        self.lbl_speed = tk.Label(prod_frame, text="Wydajność Linii: 100%", font=("Consolas", 14, "bold"), bg="#34495e", fg="#2ecc71")
        self.lbl_speed.pack(pady=10)

        tk.Label(prod_frame, text="Ruch taśmociągu:", bg="#34495e", fg="white").pack(anchor="w")
        
        # Pasek postępu symulujący ruch linii
        self.belt_progress = ttk.Progressbar(prod_frame, orient="horizontal", length=350, mode="determinate")
        self.belt_progress.pack(pady=10)

        self.lbl_count = tk.Label(prod_frame, text="Wyprodukowane detale: 0", font=("Consolas", 16, "bold"), bg="#34495e", fg="#f1c40f")
        self.lbl_count.pack(pady=20)

        # --- Dolny panel: Dziennik Zdarzeń ---
        log_frame = tk.Frame(self.root, bg="#2c3e50")
        log_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(log_frame, text="Dziennik zdarzeń systemowych:", bg="#2c3e50", fg="#bdc3c7").pack(anchor="w")
        self.log_area = tk.Text(log_frame, height=8, state="disabled", bg="#1a252f", fg="#2ecc71", font=("Consolas", 10))
        self.log_area.pack(fill="x")

    def log(self, msg):
        self.log_area.config(state="normal")
        self.log_area.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def start_monitoring(self):
        self.is_running = True
        self.log("System uruchomiony. Rozpoczęto produkcję.")
        self.run_process_loop()
        self.schedule_autodiagnostics()

    def run_process_loop(self):
        if not self.is_running: return
        
        # Pobieranie rzeczywistych parametrów PC
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        # Symulacja temperatury bazująca na obciążeniu PC (brak uniwersalnego odczytu temp. w psutil na Windows)
        temp = 45 + (cpu * 0.4) + (ram * 0.1) + random.uniform(-1, 2)
        
        # Aktualizacja interfejsu diagnostyki
        self.lbl_cpu.config(text=f"Obciążenie CPU: {cpu}%")
        self.lbl_ram.config(text=f"Zajętość RAM: {ram}%")
        self.lbl_temp.config(text=f"Temp. Napędów: {temp:.1f}°C")
        
        # LOGIKA REAKCJI NA PARAMETRY
        if temp > 75:
            self.status_box.config(text="ALARM: PRZEGRZANIE", bg="#e74c3c")
            self.lbl_fans.config(text="Wentylatory: AWARYJNE MAX", fg="#e74c3c")
            self.line_efficiency = 30 # Znaczne zwolnienie produkcji
            self.cooling_active = True
            self.log("KRYTYCZNE PRZEGRZANIE! Wymuszone chłodzenie. Redukcja prędkości do 30%.")
            
        elif temp > 60:
            self.status_box.config(text="OSTRZEŻENIE: WYSOKA TEMP", bg="#f39c12")
            self.lbl_fans.config(text="Wentylatory: POMOCNICZE [ON]", fg="#f39c12")
            self.line_efficiency = 70
            self.cooling_active = True
            self.log("Wysoka temperatura. Włączono chłodzenie pomocnicze (wydajność 70%).")
            
        else:
            self.status_box.config(text="PRACA NOMINALNA", bg="#27ae60")
            self.lbl_fans.config(text="Wentylatory: GŁÓWNE [ON]", fg="#3498db")
            self.line_efficiency = 100
            if self.cooling_active:
                self.log("Temperatura ustabilizowana. Powrót do pracy nominalnej.")
                self.cooling_active = False

        # Aktualizacja wizualizacji produkcji
        self.lbl_speed.config(text=f"Wydajność Linii: {self.line_efficiency}%")
        
        # Ruch taśmy (zależny od wydajności)
        step = (self.line_efficiency / 100.0) * 20
        self.belt_position += step
        
        if self.belt_position >= 100:
            self.belt_position = 0
            self.production_count += 1
            self.lbl_count.config(text=f"Wyprodukowane detale: {self.production_count}")
            
        self.belt_progress['value'] = self.belt_position
        
        # Losowe awarie (ok. 2% szansy)
        if random.random() < 0.02:
            self.trigger_random_failure()

        self.root.after(1000, self.run_process_loop)

    def trigger_random_failure(self):
        self.is_running = False
        self.status_box.config(text="AWARIA LINII", bg="#c0392b")
        error_types = ["Zacięcie materiału w sekcji 2", "Błąd pozycjonowania lasera", "Spadek ciśnienia pneumatyki"]
        error_msg = random.choice(error_types)
        
        self.log(f"AWARIA: {error_msg}. Zatrzymano linię!")
        messagebox.showwarning("AWARIA SPRZĘTOWA", f"{error_msg}\n\nProdukcja wstrzymana. Wymagana interwencja operatora!")
        
        # Wznowienie po zamknięciu okna komunikatu
        self.is_running = True
        self.log("Awaria usunięta przez operatora. Wznawianie produkcji...")
        self.run_process_loop()

    def schedule_autodiagnostics(self):
        # Okresowe sprawdzanie obecności (co 20-40 sekund)
        delay = random.randint(20000, 40000)
        self.root.after(delay, self.presence_check)

    def presence_check(self):
        if not self.is_running: return
        
        self.log("PROCEDURA AUTODIAGNOSTYKI: Oczekiwanie na operatora...")
        
        check_win = tk.Toplevel(self.root)
        check_win.title("WERYFIKACJA")
        check_win.geometry("300x150")
        check_win.attributes("-topmost", True)
        check_win.configure(bg="#e67e22")
        
        tk.Label(check_win, text="POTWIERDŹ OBECNOŚĆ\nWciśnij przycisk lub klawisz F1\n(Czas: 30s)", font=("Arial", 11, "bold"), bg="#e67e22").pack(pady=20)
        
        status = {"responded": False}

        def on_confirm(event=None):
            status["responded"] = True
            check_win.destroy()
            self.log("Autodiagnostyka pomyślna. Czuwanie operatora potwierdzone.")
            self.schedule_autodiagnostics()

        btn = tk.Button(check_win, text="POTWIERDZAM (F1)", command=on_confirm, bg="#2c3e50", fg="white", font=("Arial", 10, "bold"))
        btn.pack()
        
        # Przypisanie klawisza F1
        check_win.bind('<F1>', on_confirm)
        check_win.focus_force() # Wymuszenie focusu na okienku, by F1 zadziałało

        # Timer 30 sekund
        def on_timeout():
            if not status["responded"]:
                check_win.destroy()
                self.is_running = False
                self.log("ALARM KRYTYCZNY! Brak operatora. Procedura awaryjnego zatrzymania.")
                messagebox.showerror("BRAK OPERATORA", "Nie potwierdzono obecności w ciągu 30s.\nZatrzymanie linii i wylogowanie z systemu!")
                self.main_frame_reset()

        self.root.after(30000, on_timeout)

    def main_frame_reset(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.is_running = False
        self.production_count = 0
        self.belt_position = 0
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = SCADASystem(root)
    root.mainloop()