import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re

class CPU:
    def __init__(self):
        # Inicjalizacja 16-bitowych rejestrów ogólnego przeznaczenia
        self.regs = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        self.pc = 0  # Program Counter
        self.program = [] # Lista instrukcji

    def get_val(self, operand):
        operand = operand.upper()
        # Tryb rejestrowy - 16 bit (nazwa rejestru + 'X' lub tylko nazwa ze zdjęcia)
        if operand in self.regs:
            return self.regs[operand]
        if operand + 'X' in self.regs:
            return self.regs[operand + 'X']
        
        # Tryb rejestrowy - 8 bit (część starsza H lub młodsza L)
        if len(operand) == 2 and operand[0] in 'ABCD' and operand[1] in 'HL':
            base_reg = operand[0]
            if operand[1] == 'H':
                return (self.regs[base_reg] >> 8) & 0xFF
            else:
                return self.regs[base_reg] & 0xFF
                
        # Tryb natychmiastowy (liczba)
        try:
            return int(operand, 0) # Obsługuje system dziesiętny i szesnastkowy (np. 0x1A)
        except ValueError:
            raise ValueError(f"Nieznany operand: {operand}")

    def set_val(self, operand, value):
        operand = operand.upper()
        # Zabezpieczenie przed wartościami ujemnymi w reprezentacji bitowej
        value = value & 0xFFFF 
        
        # Obsługa głównego rejestru (np. A)
        if operand in self.regs:
            self.regs[operand] = value
        elif operand + 'X' in self.regs:
            self.regs[operand + 'X'] = value
        elif len(operand) == 2 and operand[0] in 'ABCD' and operand[1] in 'HL':
            base_reg = operand[0]
            current_val = self.regs[base_reg]
            if operand[1] == 'H':
                # Zeruj starszy bajt, wpisz nową wartość
                self.regs[base_reg] = (current_val & 0x00FF) | ((value & 0xFF) << 8)
            else:
                # Zeruj młodszy bajt, wpisz nową wartość
                self.regs[base_reg] = (current_val & 0xFF00) | (value & 0xFF)
        else:
            raise ValueError(f"Nieprawidłowy operand docelowy: {operand}")

    def execute_instruction(self, instruction):
        # Usuwanie komentarzy i zbędnych spacji
        instruction = instruction.split(';')[0].strip()
        if not instruction:
            return

        # Parsing instrukcji
        match = re.match(r'([A-Z]+)\s+([A-Z0-9]+)\s*,\s*([A-Z0-9x]+)', instruction, re.IGNORECASE)
        if not match:
            raise ValueError(f"Błąd składni w instrukcji: {instruction}")

        cmd, dest, src = match.groups()
        cmd = cmd.upper()

        src_val = self.get_val(src)

        if cmd == 'MOV':
            self.set_val(dest, src_val)
        elif cmd == 'ADD':
            dest_val = self.get_val(dest)
            self.set_val(dest, dest_val + src_val)
        elif cmd == 'SUB':
            dest_val = self.get_val(dest)
            self.set_val(dest, dest_val - src_val)
        else:
            raise ValueError(f"Nieznany rozkaz: {cmd}")

    def reset(self):
        self.regs = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        self.pc = 0

class SimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Symulator Mikroprocesora 16-bit")
        self.geometry("1000x700")
        self.cpu = CPU()
        self.led_size = 15
        self.create_widgets()
        self.update_ui()

    def create_widgets(self):
        # --- Lewa strona (Wizualna) ---
        visual_frame = tk.Frame(self)
        visual_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Wizualizacja rejestrów
        self.create_register_visuals(visual_frame)

        # Wizualizacja argumentu natychmiastowego
        self.create_argument_visual(visual_frame)

        # Sekcja wejściowa instrukcji
        self.create_input_section(visual_frame)

        # --- Prawa strona (Tekstowa i Sterowanie) ---
        text_frame = tk.Frame(self, width=300)
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=20, pady=20)

        tk.Label(text_frame, text="Kod Programu", font=("Arial", 16, "bold")).pack(pady=(0, 10))

        self.program_frame = tk.Frame(text_frame)
        self.program_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.program_frame)
        self.program_list = tk.Listbox(self.program_frame, font=("Courier", 12), yscrollcommand=scrollbar.set, selectbackground="lightblue", selectforeground="black")
        self.program_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.program_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.program_list.bind('<<ListboxSelect>>', self.on_listbox_select) # Aktualizacja argumentu przy zaznaczaniu

        # Przyciski sterujące
        control_frame = tk.Frame(text_frame, pady=20)
        control_frame.pack(fill=tk.X)
        
        tk.Button(control_frame, text="Wykonaj krok", command=self.step_execution, bg="lightblue").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Wykonaj program", command=self.full_execution, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Zresetuj CPU", command=self.reset_cpu, bg="lightcoral").pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Wyczyść program", command=self.clear_program).pack(side=tk.LEFT, padx=5)

        file_frame = tk.Frame(text_frame)
        file_frame.pack(fill=tk.X)
        tk.Button(file_frame, text="Zapisz program", command=self.save_file).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Wczytaj program", command=self.load_file).pack(side=tk.LEFT, padx=5)

    def create_register_visuals(self, parent):
        regs_frame = tk.LabelFrame(parent, text="Rejestry Procesora", padx=10, pady=10)
        regs_frame.pack(fill=tk.X, pady=(0, 20))

        self.reg_leds = {}
        self.reg_bin_entries = {}

        for reg_name in ['A', 'B', 'C', 'D']:
            frame = tk.Frame(regs_frame, pady=10)
            frame.pack(fill=tk.X)

            tk.Label(frame, text=reg_name, font=("Arial", 16, "bold"), width=3, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 10))

            led_container = tk.Frame(frame)
            led_container.pack(side=tk.LEFT)
            self.create_led_row(led_container, reg_name, 0)
            self.create_led_row(led_container, reg_name, 1)

            entry = tk.Entry(frame, font=("Courier", 12), width=20, state="readonly")
            entry.pack(side=tk.LEFT, padx=10)
            self.reg_bin_entries[reg_name] = entry

            tk.Button(frame, text="WPISZ", command=lambda r=reg_name: self.write_to_register(r)).pack(side=tk.LEFT, padx=(5,0))

            hl_frame = tk.Frame(frame)
            hl_frame.pack(side=tk.LEFT, padx=(10, 0))
            tk.Label(hl_frame, text=f"{reg_name}H", font=("Courier", 10)).pack(side=tk.LEFT)
            tk.Label(hl_frame, text=" | ", font=("Courier", 10)).pack(side=tk.LEFT)
            tk.Label(hl_frame, text=f"{reg_name}L", font=("Courier", 10)).pack(side=tk.LEFT)

    def create_led_row(self, parent, reg_name, val):
        row_frame = tk.Frame(parent)
        row_frame.pack(fill=tk.X, anchor=tk.W)
        
        # Diody od bocznej 15 do 0
        row_leds = []
        for i in range(15, -1, -1):
            canvas = tk.Canvas(row_frame, width=self.led_size+2, height=self.led_size+2)
            canvas.pack(side=tk.LEFT)
            circle = canvas.create_oval(1, 1, self.led_size, self.led_size, outline="gray", fill="lightgray")
            row_leds.append((canvas, circle))
        
        # Przechowujemy diody w slowniku [nazwa_rejestru][wartość]
        if reg_name not in self.reg_leds:
            self.reg_leds[reg_name] = {}
        self.reg_leds[reg_name][val] = row_leds

    def create_argument_visual(self, parent):
        arg_frame = tk.LabelFrame(parent, text="Argument dla trybu natychmiastowego (podgląd)", padx=10, pady=10)
        arg_frame.pack(fill=tk.X, pady=(0, 20))

        self.arg_leds = {}
        
        led_container = tk.Frame(arg_frame)
        led_container.pack(fill=tk.X)
        self.create_led_row_simple(led_container, 'ARG', 0)
        self.create_led_row_simple(led_container, 'ARG', 1)

        bin_frame = tk.Frame(arg_frame)
        bin_frame.pack(fill=tk.X, pady=5)
        
        self.arg_bin_entry = tk.Entry(bin_frame, font=("Courier", 12), width=20, state="readonly")
        self.arg_bin_entry.pack(side=tk.LEFT, padx=10)

        tk.Label(bin_frame, text="in H", font=("Courier", 10)).pack(side=tk.LEFT)
        tk.Label(bin_frame, text=" | ", font=("Courier", 10)).pack(side=tk.LEFT)
        tk.Label(bin_frame, text="in L", font=("Courier", 10)).pack(side=tk.LEFT)

    def create_led_row_simple(self, parent, reg_name, val):
        row_frame = tk.Frame(parent)
        row_frame.pack(fill=tk.X, anchor=tk.W)
        row_leds = []
        for i in range(15, -1, -1):
            canvas = tk.Canvas(row_frame, width=self.led_size+2, height=self.led_size+2)
            canvas.pack(side=tk.LEFT)
            circle = canvas.create_oval(1, 1, self.led_size, self.led_size, outline="gray", fill="lightgray")
            row_leds.append((canvas, circle))
        
        if reg_name not in self.arg_leds:
            self.arg_leds[reg_name] = {}
        self.arg_leds[reg_name][val] = row_leds

    def create_input_section(self, parent):
        input_frame = tk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(input_frame, text="Dodaj instrukcję:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        # Proste pole tekstowe dla zachowania elastyczności parsingu
        self.instr_entry = tk.Entry(input_frame, font=("Courier", 12), width=30)
        self.instr_entry.pack(side=tk.LEFT)
        self.instr_entry.insert(0, "MOV AX, 0x1A")
        tk.Button(input_frame, text="Dodaj instrukcję", command=self.add_instruction).pack(side=tk.LEFT, padx=5)

    def update_ui(self):
        # Aktualizacja wizualna rejestrów
        for reg_name in ['A', 'B', 'C', 'D']:
            val = self.cpu.regs[reg_name]
            binary_str = f"{val:016b}"
            
            # Pole tekstowe binarne
            entry = self.reg_bin_entries[reg_name]
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, f"{binary_str[:8]} {binary_str[8:]}") # Dodane spacje dla czytelności
            entry.config(state="readonly")
            
            # Diody LED
            for bit_index in range(16):
                bit = (val >> (15 - bit_index)) & 1
                
                # Rząd dla '0'
                canvas0, circle0 = self.reg_leds[reg_name][0][bit_index]
                canvas0.itemconfig(circle0, fill="lightgray" if bit == 1 else "lightgray") # To pole jest nielogiczne na zdjeciu, na zdjeciu sa puste kolka dla zera. Ustawie na stale jasnoszary, bo to brak sygnalu.
                
                # Rząd dla '1' (zielone, jeśli bit jest ustawiony)
                canvas1, circle1 = self.reg_leds[reg_name][1][bit_index]
                canvas1.itemconfig(circle1, fill="green" if bit == 1 else "lightgray")

        # Zaznaczanie aktywnej linii kodu (tryb krokowy)
        self.program_list.selection_clear(0, tk.END)
        if 0 <= self.cpu.pc < len(self.cpu.program):
            self.program_list.selection_set(self.cpu.pc)
            self.program_list.see(self.cpu.pc)

    def update_argument_visual(self, val):
        if val is None:
            # Wyczyść
            self.arg_bin_entry.config(state="normal")
            self.arg_bin_entry.delete(0, tk.END)
            self.arg_bin_entry.config(state="readonly")
            for bit_index in range(16):
                 self.arg_leds['ARG'][1][bit_index][0].itemconfig(self.arg_leds['ARG'][1][bit_index][1], fill="lightgray")
            return

        binary_str = f"{val:016b}"
        self.arg_bin_entry.config(state="normal")
        self.arg_bin_entry.delete(0, tk.END)
        self.arg_bin_entry.insert(0, f"{binary_str[:8]} {binary_str[8:]}")
        self.arg_bin_entry.config(state="readonly")

        for bit_index in range(16):
            bit = (val >> (15 - bit_index)) & 1
            self.arg_leds['ARG'][1][bit_index][0].itemconfig(self.arg_leds['ARG'][1][bit_index][1], fill="green" if bit == 1 else "lightgray")

    def on_listbox_select(self, event):
        # Sprawdza, czy instrukcja ma argument natychmiastowy i aktualizuje wizualizacje
        if not self.program_list.curselection():
            return
        index = self.program_list.curselection()[0]
        instr = self.cpu.program[index]
        
        match = re.search(r',\s*([0-9]+|0x[0-9A-Fa-f]+)', instr) # Szuka liczby dziesietnej lub szesnastkowej
        if match:
             val_str = match.group(1)
             try:
                 val = int(val_str, 0)
                 self.update_argument_visual(val)
             except ValueError:
                 self.update_argument_visual(None)
        else:
             self.update_argument_visual(None)

    def add_instruction(self):
        instr = self.instr_entry.get().strip()
        if instr:
            # Dodanie do listy GUI z numeracją (np. "01: MOV AX, 0x1A")
            idx = len(self.cpu.program) + 1
            self.program_list.insert(tk.END, f"{idx:02d}: {instr}")
            self.cpu.program.append(instr)
            self.instr_entry.delete(0, tk.END)

    def step_execution(self):
        if self.cpu.pc < len(self.cpu.program):
            instr = self.cpu.program[self.cpu.pc]
            try:
                self.cpu.execute_instruction(instr)
                self.cpu.pc += 1
                self.update_ui()
                # Aktualizacja wizualizacji argumentu przy kroku (jeśli zaznaczona instrukcja to ta aktualna)
                # self.program_list.selection_set(self.cpu.pc-1) # To by zaznaczalo wykonana
                if self.program_list.curselection() and self.program_list.curselection()[0] == self.cpu.pc-1:
                    self.on_listbox_select(None)

            except Exception as e:
                messagebox.showerror("Błąd wykonania", f"Linia {self.cpu.pc+1}: {str(e)}")
        else:
            messagebox.showinfo("Koniec", "Program zakończył działanie.")

    def full_execution(self):
        while self.cpu.pc < len(self.cpu.program):
            self.step_execution()

    def reset_cpu(self):
        self.cpu.reset()
        self.update_ui()

    def clear_program(self):
        self.cpu.program.clear()
        self.program_list.delete(0, tk.END)
        self.reset_cpu()
        self.update_argument_visual(None)

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Pliki tekstowe", "*.txt")])
        if path:
            with open(path, 'w') as f:
                for line in self.cpu.program:
                    f.write(line + '\n')

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki tekstowe", "*.txt")])
        if path:
            self.clear_program()
            with open(path, 'r') as f:
                for line in f:
                    # Dodaj instrukcję do edytora
                    self.instr_entry.delete(0, tk.END)
                    self.instr_entry.insert(0, line.strip())
                    self.add_instruction()

    def write_to_register(self, reg_name):
        # Funkcja dla przycisku WPISZ po lewej (nielogiczna przy edytorze kodu, ale na zdjeciu jest)
        binary_str = self.reg_bin_entries[reg_name].get().replace(" ", "")
        try:
             val = int(binary_str, 2)
             self.cpu.set_val(reg_name, val)
             self.update_ui()
        except ValueError:
             messagebox.showerror("Błąd wpisu", "Nieprawidłowy format binarny.")

if __name__ == "__main__":
    app = SimulatorGUI()
    app.mainloop()