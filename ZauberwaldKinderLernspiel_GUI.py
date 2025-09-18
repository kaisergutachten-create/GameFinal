# KinderLernspiel_Zauberwald_Sound.py
# Zauberwald – Hexen, Drachen & Magie (mit Sounds)
# Windows-GUI-Spiel für Kinder (~3 Jahre): Zählen, Drachen fangen, Memory & Logik.
# Nur Standardbibliothek (tkinter, random, time, winsound [Windows]).
# Start: python KinderLernspiel_Zauberwald_Sound.py
# EXE:   py -m PyInstaller --onefile --windowed KinderLernspiel_Zauberwald_Sound.py

import tkinter as tk
from tkinter import ttk
import random
import time

# Optionaler Sound (Windows)
try:
    import winsound
    HAS_SOUND = True
except Exception:
    HAS_SOUND = False

APP_TITLE = "Zauberwald – Hexen, Drachen & Magie (mit Sound)"
BG = "#fbf7ff"
CARD = "#ffffff"
PRIMARY = "#7c3aed"   # Violett
SUCCESS = "#16a34a"
WARN = "#f59e0b"
TEXT = "#1f1147"

LARGE_BTN_FONT = ("Segoe UI", 18, "bold")
MID_BTN_FONT = ("Segoe UI", 16, "bold")
BIG_FONT = ("Segoe UI", 32, "bold")
MID_FONT = ("Segoe UI", 20, "bold")

MAGIC_CREATURES = ["🧙‍♀️","🐉","🧚","🦄","🧙‍♂️","🐲"]
MAGIC_EMOJIS = MAGIC_CREATURES + ["✨","🔮","🪄","🧪","🌟","🌈"]

def safe_beep(freq=800, dur_ms=150):
    if HAS_SOUND:
        try:
            winsound.Beep(int(freq), int(dur_ms))
        except Exception:
            pass

def sound_success():
    # kleine aufsteigende Melodie
    for f in (880, 1100, 1320):
        safe_beep(f, 120)

def sound_fail():
    for f in (300, 250):
        safe_beep(f, 180)

def sound_reward():
    for f in (880, 980, 1240, 1560):
        safe_beep(f, 120)

def sound_click():
    safe_beep(950, 40)

class StickerBar(ttk.Frame):
    def __init__(self, master, goal=5, sound_on=True):
        super().__init__(master, padding=(8,6))
        self.goal = goal
        self.counter = 0
        self.stickers = 0
        self.sound_on = sound_on
        self.configure(style="Flat.TFrame")

        ttk.Label(self, text="Sticker:", style="Info.TLabel").grid(row=0, column=0, sticky="w")
        self.sticker_lbl = ttk.Label(self, text="", style="Big.TLabel")
        self.sticker_lbl.grid(row=0, column=1, sticky="w", padx=(8,0))
        self.progress = ttk.Progressbar(self, length=160, maximum=self.goal)
        self.progress.grid(row=0, column=2, padx=(12,0))

    def add_point(self):
        self.counter += 1
        self.progress["value"] = self.counter
        if self.counter >= self.goal:
            self.counter = 0
            self.stickers += 1
            self.progress["value"] = 0
            self.sticker_lbl.configure(text="🌟" * self.stickers)
            return True
        return False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=BG)
        self.geometry("980x660")
        self.minsize(860, 580)

        self._style()
        self.sound_enabled = True  # Toggle für Ton

        # Header
        header = ttk.Frame(self, padding=12, style="Flat.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="🪄 Zauberwald", style="Title.TLabel").pack(side="left")
        self.sticker_bar = StickerBar(header, goal=5, sound_on=self.sound_enabled)
        self.sticker_bar.pack(side="right")

        # Navigation
        nav = ttk.Frame(self, padding=(12,6), style="Flat.TFrame")
        nav.pack(fill="x")
        ttk.Button(nav, text="🔢 Zauber-Zählen", style="Primary.TButton", command=self.show_count).pack(side="left", padx=(0,8))
        ttk.Button(nav, text="🐉 Drachen fangen", style="Primary.TButton", command=self.show_catch).pack(side="left", padx=8)
        ttk.Button(nav, text="🃏 Zauber-Paare", style="Primary.TButton", command=self.show_memory).pack(side="left", padx=8)
        ttk.Button(nav, text="🧠 Magie-Logik", style="Primary.TButton", command=self.show_logic).pack(side="left", padx=8)
        ttk.Button(nav, text="🔀 Mix", command=self.random_game).pack(side="left", padx=(16,0))

        # Sound Toggle
        self.sound_btn = ttk.Button(nav, text="🔊 Ton: AN", command=self.toggle_sound)
        self.sound_btn.pack(side="right")

        self.status = ttk.Label(self, text="Willkommen im Zauberwald! ✨", style="Info.TLabel", anchor="center")
        self.status.pack(fill="x", padx=12)

        # Content container
        self.container = ttk.Frame(self, padding=12, style="Flat.TFrame")
        self.container.pack(expand=True, fill="both")
        self.frames = {}
        for F in (CountPage, CatchDragonPage, MemoryPage, LogicPage):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.correct_total = 0
        self.incorrect_total = 0
        self.show_count()

        # Footer
        footer = ttk.Frame(self, padding=12, style="Flat.TFrame")
        footer.pack(fill="x")
        self.score_lbl = ttk.Label(footer, text=self._score_text(), style="Info.TLabel")
        self.score_lbl.pack(side="left")
        ttk.Button(footer, text="Neues Spiel", command=self.reset).pack(side="right")

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.sound_btn.configure(text="🔊 Ton: AN" if self.sound_enabled else "🔇 Ton: AUS")
        if self.sound_enabled:
            sound_click()

    def _style(self):
        style = ttk.Style(self)
        style.configure("Flat.TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 22, "bold"))
        style.configure("Big.TLabel", background=BG, foreground=TEXT, font=BIG_FONT)
        style.configure("Info.TLabel", background=BG, foreground=TEXT, font=MID_FONT)
        style.configure("CardTitle.TLabel", background=CARD, foreground=TEXT, font=MID_FONT)
        style.configure("Result.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 24, "bold"))
        style.configure("Primary.TButton", font=MID_BTN_FONT)
        style.configure("TButton", font=MID_BTN_FONT)

    def show_frame(self, name):
        self.frames[name].tkraise()
        self.frames[name].new_round()

    def show_count(self):
        self.show_frame("CountPage")
        self.status.configure(text="🔢 Zähle die Zauberwesen und tippe die richtige Zahl!")

    def show_catch(self):
        self.show_frame("CatchDragonPage")
        self.status.configure(text="🐉 Klicke den Drachen, bevor er wegfliegt!")

    def show_memory(self):
        self.show_frame("MemoryPage")
        self.status.configure(text="🃏 Finde die Paare im Zauber-Memory!")

    def show_logic(self):
        self.show_frame("LogicPage")
        self.status.configure(text="🧠 Was passt nicht? Oder welche Form stimmt?")

    def random_game(self):
        choice = random.choice(["CountPage","CatchDragonPage","MemoryPage","LogicPage"])
        self.show_frame(choice)
        self.status.configure(text="🔀 Zauber-Mix! Viel Spaß!")
        if self.sound_enabled:
            sound_click()

    def handle_result(self, ok, frame):
        if ok:
            self.correct_total += 1
            frame.flash(True)
            if self.sound_enabled:
                sound_success()
            got = self.sticker_bar.add_point()
            if got:
                self.status.configure(text="🎉 Bravo! Ein neuer Zauber-Sticker! 🌟")
                if self.sound_enabled:
                    sound_reward()
            else:
                self.status.configure(text=random.choice(["Toll gemacht! ✨","Zauberhaft! 😊","Super! 💫","Klasse! 👏"]))
        else:
            self.incorrect_total += 1
            frame.flash(False)
            self.status.configure(text=random.choice(["Fast! Nochmal! 🙂","Das schaffst du! 💪"]))
            if self.sound_enabled:
                sound_fail()
        self.score_lbl.configure(text=self._score_text())

    def _score_text(self):
        return f"Richtig: {self.correct_total}   |   Versuche: {self.correct_total + self.incorrect_total}"

    def reset(self):
        self.correct_total = 0
        self.incorrect_total = 0
        self.sticker_bar.counter = 0
        self.sticker_bar.stickers = 0
        self.sticker_bar.progress['value'] = 0
        self.sticker_bar.sticker_lbl.configure(text="")
        self.score_lbl.configure(text=self._score_text())
        self.status.configure(text="Neustart im Zauberwald! 🌈")
        for f in self.frames.values():
            f.new_round()
        if self.sound_enabled:
            sound_click()


class BasePage(ttk.Frame):
    def __init__(self, master, app: App):
        super().__init__(master, padding=16, style="Card.TFrame")
        self.app = app
        self.card = ttk.Frame(self, padding=16, style="Card.TFrame")
        self.card.pack(expand=True, fill="both")

        self.title_lbl = ttk.Label(self.card, text="", style="CardTitle.TLabel")
        self.title_lbl.pack()

        self.canvas = tk.Canvas(self.card, bg="white", height=260, highlightthickness=0)
        self.canvas.pack(pady=8, fill="x")

        self.buttons_frame = ttk.Frame(self.card, padding=(0,8), style="Card.TFrame")
        self.buttons_frame.pack()

        self.feedback = ttk.Label(self.card, text="", style="Result.TLabel")
        self.feedback.pack(pady=4)

    def clear_buttons(self):
        for w in self.buttons_frame.winfo_children():
            w.destroy()

    def flash(self, good=True):
        color = "#d1fae5" if good else "#fee2e2"
        orig = self.canvas["bg"]
        self.canvas.configure(bg=color)
        self.canvas.update_idletasks()
        self.after(180, lambda: self.canvas.configure(bg=orig))


class CountPage(BasePage):
    """Zähle 1–6 Zauberwesen (Emojis) und wähle die richtige Zahl."""
    def new_round(self):
        self.title_lbl.configure(text="Zähle die Zauberwesen und tippe die Zahl!")
        self.feedback.configure(text="")
        self.clear_buttons()
        self.canvas.delete("all")

        count = random.randint(1, 6)
        emojis = random.choices(MAGIC_EMOJIS, k=count)
        x = 80
        for e in emojis:
            self.canvas.create_text(x, 130, text=e, font=("Segoe UI Emoji", 64))
            x += 120

        options = {count}
        while len(options) < 4:
            options.add(random.randint(1, 6))
        opts = list(options)
        random.shuffle(opts)

        for n in opts:
            ttk.Button(self.buttons_frame, text=str(n), style="Primary.TButton",
                       command=lambda n=n: self.check(n, count)).pack(side="left", padx=8, pady=6)

    def check(self, val, correct):
        if val == correct:
            self.feedback.configure(text="Richtig! 🎉", foreground=SUCCESS)
            self.app.handle_result(True, self)
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Nochmal schauen! 🙂", foreground=WARN)
            self.app.handle_result(False, self)


class CatchDragonPage(BasePage):
    """Klicke den Drachen, bevor er woanders auftaucht. 5x fangen = Runde gewonnen."""
    def __init__(self, master, app: App):
        super().__init__(master, app)
        self.running = False
        self.catches = 0
        self.dragon_id = None
        self.dragon_pos = (0,0)
        self.canvas.bind("<Button-1>", self.on_click)

    def new_round(self):
        self.title_lbl.configure(text="Fang den Drachen! Klicke ihn 5-mal!")
        self.feedback.configure(text="")
        self.clear_buttons()
        self.canvas.delete("all")
        self.catches = 0
        self.running = False
        ttk.Button(self.buttons_frame, text="Start", style="Primary.TButton", command=self.start_round).pack(side="left", padx=8, pady=6)

    def start_round(self):
        self.running = True
        if self.app.sound_enabled:
            sound_click()
        self.move_dragon()

    def move_dragon(self):
        if not self.running:
            return
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 960
        h = self.canvas.winfo_height() or 260
        x = random.randint(60, w-60)
        y = random.randint(60, h-60)
        self.dragon_pos = (x, y)
        self.dragon_id = self.canvas.create_text(x, y, text="🐉", font=("Segoe UI Emoji", 72))
        # funken
        for _ in range(6):
            fx = x + random.randint(-80, 80)
            fy = y + random.randint(-80, 80)
            self.canvas.create_text(fx, fy, text=random.choice(["✨","🌟","🪄"]), font=("Segoe UI Emoji", 18))
        # nach kurzer Zeit weiterfliegen
        self.after(900, self.move_dragon)

    def on_click(self, event):
        if not self.running or self.dragon_id is None:
            return
        x, y = self.dragon_pos
        # einfache Trefferzone (Rechteck um den Drachen)
        if abs(event.x - x) < 50 and abs(event.y - y) < 50:
            self.catches += 1
            self.feedback.configure(text=f"Gefangen! ({self.catches}/5) 🎉", foreground=SUCCESS)
            if self.app.sound_enabled:
                sound_success()
            if self.catches >= 5:
                self.running = False
                self.app.handle_result(True, self)
                self.after(800, self.new_round)
        else:
            self.feedback.configure(text="Knapp daneben! 😉", foreground=WARN)
            self.app.handle_result(False, self)
            if self.app.sound_enabled:
                sound_fail()


class MemoryPage(BasePage):
    """Zauber-Memory mit 6 Karten (3 Paare)."""
    def __init__(self, master, app: App):
        super().__init__(master, app)
        self.cards = []      # list of (btn, value, revealed, matched)
        self.first = None    # index of first revealed
        self.lock = False

    def new_round(self):
        self.title_lbl.configure(text="Finde die Paare!")
        self.feedback.configure(text="")
        self.canvas.delete("all")
        self.clear_buttons()
        self.cards = []
        self.first = None
        self.lock = False

        pool = random.sample(MAGIC_CREATURES, 3)
        values = pool + pool
        random.shuffle(values)

        grid = ttk.Frame(self.card, padding=(0,8), style="Card.TFrame")
        grid.pack()
        self.grid_frame = grid

        for i, val in enumerate(values):
            btn = ttk.Button(grid, text="🂠", width=4, command=lambda i=i: self.flip(i))
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)
            self.cards.append([btn, val, False, False])

    def flip(self, i):
        if self.lock: return
        btn, val, rev, matched = self.cards[i]
        if matched or rev: return

        # aufdecken
        btn.configure(text=val)
        self.cards[i][2] = True
        if self.app.sound_enabled:
            sound_click()

        if self.first is None:
            self.first = i
            return

        # zweites
        j = self.first
        self.first = None

        if self.cards[i][1] == self.cards[j][1]:
            # match
            self.cards[i][3] = True
            self.cards[j][3] = True
            self.feedback.configure(text="Ein Paar! ✨", foreground=SUCCESS)
            self.app.handle_result(True, self)
            if self.app.sound_enabled:
                sound_success()
            # gewonnen?
            if all(c[3] for c in self.cards):
                if self.app.sound_enabled:
                    sound_reward()
                self.after(800, self.new_round)
        else:
            # kurz zeigen, dann verdecken
            self.lock = True
            self.feedback.configure(text="Nicht gleich – merk's dir! 🙂", foreground=WARN)
            self.app.handle_result(False, self)
            if self.app.sound_enabled:
                sound_fail()
            self.after(900, lambda: self.hide(i, j))

    def hide(self, i, j):
        for idx in (i, j):
            self.cards[idx][2] = False
            self.cards[idx][0].configure(text="🂠")
        self.lock = False


class LogicPage(BasePage):
    """Zwei Modi: (A) Was passt nicht? (B) Form zuordnen (Zauberformen)."""
    def new_round(self):
        self.feedback.configure(text="")
        self.clear_buttons()
        self.canvas.delete("all")
        mode = random.choice(["odd_one_out","shape_match"])
        if mode == "odd_one_out":
            self.title_lbl.configure(text="Was passt nicht?")
            self.odd_one_out()
        else:
            self.title_lbl.configure(text="Welche Form passt?")
            self.shape_match()

    def odd_one_out(self):
        group1 = ["🧙‍♀️","🧙‍♂️","🧚","🦄"]
        group2 = ["🍎","🍌","🍓","🍐"]
        group3 = ["🚗","✈️","🚲","🚂"]
        groups = [group1, group2, group3]
        g = random.choice(groups)
        others = [x for x in groups if x is not g]
        same = random.choice(g)
        odd = random.choice(random.choice(others))
        items = [same, same, same, odd]
        random.shuffle(items)
        for i, e in enumerate(items):
            x = 240 * i + 120
            self.canvas.create_text(x, 130, text=e, font=("Segoe UI Emoji", 72))
        for i, e in enumerate(items):
            ttk.Button(self.buttons_frame, text=str(i+1), style="Primary.TButton",
                       command=lambda e=e, same=same: self.check_odd(e, same)).pack(side="left", padx=8, pady=6)

    def check_odd(self, chosen, same):
        if chosen != same:
            self.feedback.configure(text="Richtig! Das ist anders. 🎉", foreground=SUCCESS)
            self.app.handle_result(True, self)
            if self.app.sound_enabled:
                sound_success()
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Schau nochmal genau hin! 🙂", foreground=WARN)
            self.app.handle_result(False, self)
            if self.app.sound_enabled:
                sound_fail()

    def shape_match(self):
        shape = random.choice(["Kreis","Quadrat","Dreieck","Herz"])
        color = random.choice(["#a78bfa","#f472b6","#34d399","#fbbf24","#60a5fa"])
        # Zeichne Referenzform
        if shape == "Kreis":
            self.canvas.create_oval(360, 50, 620, 310, fill=color, width=0)
        elif shape == "Quadrat":
            self.canvas.create_rectangle(360, 50, 620, 310, fill=color, width=0)
        elif shape == "Dreieck":
            self.canvas.create_polygon(490, 50, 360, 310, 620, 310, fill=color, width=0)
        else: # Herz (zwei Kreise + Dreieck)
            self.canvas.create_oval(380, 70, 510, 200, fill=color, width=0)
            self.canvas.create_oval(510, 70, 640, 200, fill=color, width=0)
            self.canvas.create_polygon(360, 180, 640, 180, 500, 320, fill=color, width=0)

        opts = ["Kreis","Quadrat","Dreieck","Herz"]
        random.shuffle(opts)
        for name in opts:
            ttk.Button(self.buttons_frame, text=name, style="Primary.TButton",
                       command=lambda name=name, shape=shape: self.check_shape(name, shape)).pack(side="left", padx=8, pady=6)

    def check_shape(self, name, shape):
        if name == shape:
            self.feedback.configure(text="Genau richtig! 💡", foreground=SUCCESS)
            self.app.handle_result(True, self)
            if self.app.sound_enabled:
                sound_success()
            self.after(700, self.new_round)
        else:
            self.feedback.configure(text="Nochmal probieren! 👀", foreground=WARN)
            self.app.handle_result(False, self)
            if self.app.sound_enabled:
                sound_fail()


if __name__ == "__main__":
    app = App()
    app.mainloop()
