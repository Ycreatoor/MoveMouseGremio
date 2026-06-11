import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyautogui
import threading
import time
import math

class MoveMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Move Mouse - Tricolor")
        self.root.geometry("400x460")
        self.root.resizable(False, False)
        
        # --- ESTILO GRÊMIO (Azul, Preto e Branco) ---
        self.azul_gremio = "#0D89E5"
        self.preto = "#000000"
        self.branco = "#FFFFFF"
        
        self.root.configure(bg=self.preto)
        
        style = ttk.Style()
        style.theme_use('clam') # Habilita customização avançada de cores
        
        # Configuração de componentes
        style.configure("TFrame", background=self.preto)
        style.configure("TLabelframe", background=self.preto, bordercolor=self.azul_gremio)
        style.configure("TLabelframe.Label", background=self.preto, foreground=self.azul_gremio, font=("Arial", 10, "bold"))
        style.configure("TLabel", background=self.preto, foreground=self.branco)
        style.configure("TCheckbutton", background=self.preto, foreground=self.branco)
        
        # Botões Azuis com texto Branco
        style.configure("TButton", background=self.azul_gremio, foreground=self.branco, font=("Arial", 10, "bold"), borderwidth=0)
        style.map("TButton", 
                  background=[("active", "#0866ab"), ("disabled", "#333333")],
                  foreground=[("disabled", "#888888")])

        # Variáveis de controle de execução
        self.running = False
        self.thread = None

        # Título Principal
        title_label = ttk.Label(root, text="Configurações do Movimento", font=("Arial", 12, "bold"), foreground=self.azul_gremio)
        title_label.pack(pady=10)

        # --- PAINEL DE MOVIMENTO E CLIQUES ---
        frame_mov = ttk.LabelFrame(root, text=" Geometria e Cliques ")
        frame_mov.pack(padx=15, pady=5, fill="x")

        ttk.Label(frame_mov, text="Circunferência do círculo (pixels):").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        self.circum_var = tk.IntVar(value=200)
        ttk.Entry(frame_mov, textvariable=self.circum_var, width=10, justify="center").grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(frame_mov, text="Quantidade de cliques por volta:").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        self.clicks_var = tk.IntVar(value=1)
        ttk.Entry(frame_mov, textvariable=self.clicks_var, width=10, justify="center").grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(frame_mov, text="Tempo para completar 1 volta (seg):").grid(row=2, column=0, padx=8, pady=6, sticky="w")
        self.lap_time_var = tk.DoubleVar(value=3.0)
        ttk.Entry(frame_mov, textvariable=self.lap_time_var, width=10, justify="center").grid(row=2, column=1, padx=8, pady=6)

        # --- PAINEL DE TEMPO DE EXECUÇÃO ---
        self.frame_time = ttk.LabelFrame(root, text=" Duração da Execução do Programa ")
        self.frame_time.pack(padx=15, pady=10, fill="x")

        self.indefinite_var = tk.BooleanVar(value=True)
        self.chk_indefinite = ttk.Checkbutton(self.frame_time, text="Tempo Indeterminado (Rodar para sempre)", 
                                              variable=self.indefinite_var, command=self.toggle_time_inputs)
        self.chk_indefinite.grid(row=0, column=0, columnspan=6, padx=8, pady=8, sticky="w")

        ttk.Label(self.frame_time, text="Horas:").grid(row=1, column=0, padx=2, pady=5, sticky="e")
        self.hours_var = tk.IntVar(value=0)
        self.entry_hours = ttk.Entry(self.frame_time, textvariable=self.hours_var, width=4, justify="center")
        self.entry_hours.grid(row=1, column=1, padx=4, pady=5)

        ttk.Label(self.frame_time, text="Min:").grid(row=1, column=2, padx=2, pady=5, sticky="e")
        self.mins_var = tk.IntVar(value=5)
        self.entry_mins = ttk.Entry(self.frame_time, textvariable=self.mins_var, width=4, justify="center")
        self.entry_mins.grid(row=1, column=3, padx=4, pady=5)

        ttk.Label(self.frame_time, text="Seg:").grid(row=1, column=4, padx=2, pady=5, sticky="e")
        self.secs_var = tk.IntVar(value=0)
        self.entry_secs = ttk.Entry(self.frame_time, textvariable=self.secs_var, width=4, justify="center")
        self.entry_secs.grid(row=1, column=5, padx=4, pady=5)

        # --- CONTROLADORES DA TELA ---
        self.status_label = ttk.Label(root, text="Status: PARADO", foreground="#FF4444", font=("Arial", 10, "bold"))
        self.status_label.pack(pady=5)

        self.timer_label = ttk.Label(root, text="Tempo restante: Infinito", font=("Arial", 9), foreground=self.branco)
        self.timer_label.pack(pady=2)

        # Botões de Ação
        btn_frame = tk.Frame(root, bg=self.preto)
        btn_frame.pack(pady=10)

        self.start_btn = ttk.Button(btn_frame, text="Iniciar", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = ttk.Button(btn_frame, text="Parar", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=10)

        self.toggle_time_inputs()

    def toggle_time_inputs(self):
        if self.indefinite_var.get():
            self.entry_hours.config(state=tk.DISABLED)
            self.entry_mins.config(state=tk.DISABLED)
            self.entry_secs.config(state=tk.DISABLED)
            self.timer_label.config(text="Tempo restante: Infinito")
        else:
            self.entry_hours.config(state=tk.NORMAL)
            self.entry_mins.config(state=tk.NORMAL)
            self.entry_secs.config(state=tk.NORMAL)
            self.timer_label.config(text="Tempo restante: Configurado")

    def move_mouse_loop(self):
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        start_time = time.time()
        
        total_seconds = 0
        if not self.indefinite_var.get():
            total_seconds = (self.hours_var.get() * 3600) + (self.mins_var.get() * 60) + self.secs_var.get()

        angle = 0
        steps = 60 
        last_second_update = -1
        
        clicks_per_lap = max(0, self.clicks_var.get())
        click_angles = [i * (2 * math.pi / clicks_per_lap) for i in range(clicks_per_lap)] if clicks_per_lap > 0 else []
        clicked_this_lap = [False] * clicks_per_lap

        while self.running:
            if not self.indefinite_var.get():
                elapsed = time.time() - start_time
                remaining = total_seconds - elapsed
                
                if remaining <= 0:
                    self.root.after(0, self.stop_by_timeout)
                    break
                
                if int(elapsed) != last_second_update:
                    last_second_update = int(elapsed)
                    hrs = int(remaining // 3600)
                    mins = int((remaining % 3600) // 60)
                    scs = int(remaining % 60)
                    self.root.after(0, lambda h=hrs, m=mins, s=scs: self.timer_label.config(
                        text=f"Tempo restante: {h:02d}:{m:02d}:{s:02d}"))

            try:
                circumference = self.circum_var.get()
                radius = circumference / (2 * math.pi)
                lap_time = self.lap_time_var.get()
                if lap_time <= 0: lap_time = 1.0
            except Exception:
                radius = 30
                lap_time = 3.0

            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            
            pyautogui.moveTo(x, y, duration=0.01)

            if clicks_per_lap > 0:
                for idx, target_angle in enumerate(click_angles):
                    if angle >= target_angle and not clicked_this_lap[idx]:
                        pyautogui.click()
                        clicked_this_lap[idx] = True

            angle += (2 * math.pi) / steps
            
            if angle >= 2 * math.pi:
                angle = 0
                clicked_this_lap = [False] * clicks_per_lap

            time.sleep(lap_time / steps)

    def start(self):
        self.running = True
        self.status_label.config(text="Status: RODANDO", foreground="#00FF00") # Verde vivo pro fundo preto
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.chk_indefinite.config(state=tk.DISABLED)
        self.entry_hours.config(state=tk.DISABLED)
        self.entry_mins.config(state=tk.DISABLED)
        self.entry_secs.config(state=tk.DISABLED)
        
        self.thread = threading.Thread(target=self.move_mouse_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.status_label.config(text="Status: PARADO", foreground="#FF4444") # Vermelho vivo pro fundo preto
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.chk_indefinite.config(state=tk.NORMAL)
        self.toggle_time_inputs()

    def stop_by_timeout(self):
        self.stop()
        messagebox.showinfo("Tempo Concluído", "O tempo programado de execução acabou. O robô foi parado com sucesso!")

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    root = tk.Tk()
    app = MoveMouseApp(root)
    root.mainloop()