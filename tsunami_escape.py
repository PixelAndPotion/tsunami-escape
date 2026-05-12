import tkinter as tk
from tkinter import scrolledtext
import random, threading, time

#  Config 
STARTING_BALANCE = 10000

#  Palette 
BG_DEEP   = "#0A0A0F"
BG_PANEL  = "#111118"
BG_INPUT  = "#18181F"
ACCENT    = "#00C2FF"       # ocean blue
ACCENT2   = "#0066AA"
DANGER    = "#FF4C4C"
GOLD      = "#FFD700"
TEXT_MAIN = "#E8E8F0"
TEXT_DIM  = "#44445A"
GREEN     = "#00FFB2"

AI_MSGS = [
    "bailed early — smart move 🏄",
    "escaped just in time 😅",
    "rode the wave like a pro 🌊",
    "didn't trust the tsunami 🏃",
    "cashed out and bought a boat ⛵",
]

#  Game logic 
def get_crash_chance(mult: float) -> float:
    if mult < 2.0:   return 0.05
    elif mult < 3.5: return 0.15
    else:            return 0.30

def simulate_ai_players():
    out = []
    for i in range(5):
        t = random.choice(["safe", "risky", "random"])
        co = (round(random.uniform(1.2, 2.0), 2) if t == "safe"
              else round(random.uniform(2.5, 5.0), 2) if t == "risky"
              else round(random.uniform(1.0, 6.0), 2))
        out.append({"name": f"Surfer{i+1}", "cash_out": co,
                    "msg": random.choice(AI_MSGS), "active": True})
    return out

#  GUI 
class TsunamiApp:
    def __init__(self, root: tk.Tk):
        self.root      = root
        self.root.title("Tsunami Escape")
        self.root.geometry("900x680")
        self.root.configure(bg=BG_DEEP)
        self.root.resizable(True, True)

        # State
        self.balance      = STARTING_BALANCE
        self.multiplier   = 1.0
        self.running      = False
        self.bet          = 0.0
        self.players      = []
        self.leaderboard  = []   # top 5 cash-out multipliers
        self.skill_active = False
        self.skill_btn    = None
        self.wave_phase   = 0    # for wave animation

        self._build()
        self._animate_wave()

    #  Layout 
    def _build(self):
        # Top bar
        bar = tk.Frame(self.root, bg=BG_PANEL, height=58)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="🌊 TSUNAMI ESCAPE",
                 font=("Courier New", 17, "bold"),
                 bg=BG_PANEL, fg=ACCENT).place(x=20, rely=0.5, anchor="w")

        self.balance_lbl = tk.Label(bar, text=f"Balance: R{self.balance:,.2f}",
                                    font=("Courier New", 12, "bold"),
                                    bg=BG_PANEL, fg=GOLD)
        self.balance_lbl.place(relx=1.0, x=-20, rely=0.5, anchor="e")

        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill=tk.X)

        # Body
        body = tk.Frame(self.root, bg=BG_DEEP)
        body.pack(fill=tk.BOTH, expand=True)

        #  Left panel 
        left = tk.Frame(body, bg=BG_PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10,4), pady=10)

        # Wave canvas
        self.wave_canvas = tk.Canvas(left, height=160, bg=BG_DEEP,
                                     highlightthickness=1,
                                     highlightbackground=ACCENT2)
        self.wave_canvas.pack(fill=tk.X, padx=12, pady=(12,0))

        # Multiplier
        self.mult_lbl = tk.Label(left, text="x1.00",
                                 font=("Courier New", 48, "bold"),
                                 bg=BG_PANEL, fg=ACCENT)
        self.mult_lbl.pack(pady=(8,0))

        self.status_lbl = tk.Label(left, text="Place a bet and start the round",
                                   font=("Courier New", 11),
                                   bg=BG_PANEL, fg=TEXT_DIM)
        self.status_lbl.pack(pady=(2,10))

        # Skill slot
        self.skill_frame = tk.Frame(left, bg=BG_PANEL, height=44)
        self.skill_frame.pack(fill=tk.X, padx=12)

        # Bet row
        bet_row = tk.Frame(left, bg=BG_INPUT)
        bet_row.pack(fill=tk.X, padx=12, pady=10)

        tk.Label(bet_row, text="R", font=("Courier New", 13, "bold"),
                 bg=BG_INPUT, fg=ACCENT).pack(side=tk.LEFT, padx=(10,2), pady=10)

        self.bet_entry = tk.Entry(bet_row, font=("Courier New", 13),
                                  bg=BG_INPUT, fg=TEXT_MAIN,
                                  insertbackground=ACCENT,
                                  relief=tk.FLAT, bd=0)
        self.bet_entry.insert(0, "100")
        self.bet_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8)

        # Quick bet buttons
        qrow = tk.Frame(left, bg=BG_PANEL)
        qrow.pack(fill=tk.X, padx=12)
        for amt in (100, 500, 1000, 5000):
            tk.Button(qrow, text=f"R{amt}",
                      font=("Courier New", 9),
                      bg=BG_INPUT, fg=TEXT_DIM,
                      activebackground=ACCENT2, activeforeground=TEXT_MAIN,
                      relief=tk.FLAT, bd=0, cursor="hand2",
                      padx=8, pady=4,
                      command=lambda a=amt: self._quick_bet(a)
                      ).pack(side=tk.LEFT, padx=(0,4), pady=6)

        # Action buttons
        btn_row = tk.Frame(left, bg=BG_PANEL)
        btn_row.pack(fill=tk.X, padx=12, pady=8)

        self.start_btn = tk.Button(btn_row, text="▶  START ROUND",
                                   font=("Courier New", 11, "bold"),
                                   bg=ACCENT2, fg=TEXT_MAIN,
                                   activebackground=ACCENT,
                                   activeforeground=BG_DEEP,
                                   relief=tk.FLAT, bd=0, cursor="hand2",
                                   padx=20, pady=10,
                                   command=self.start_round)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,6))

        self.cash_btn = tk.Button(btn_row, text="🏄  ESCAPE NOW",
                                  font=("Courier New", 11, "bold"),
                                  bg=DANGER, fg=TEXT_MAIN,
                                  activebackground="#FF7777",
                                  activeforeground=BG_DEEP,
                                  relief=tk.FLAT, bd=0, cursor="hand2",
                                  padx=20, pady=10,
                                  state=tk.DISABLED,
                                  command=self.cash_out)
        self.cash_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Log
        tk.Frame(left, bg=ACCENT2, height=1).pack(fill=tk.X, padx=12, pady=(8,4))
        tk.Label(left, text="GAME LOG", font=("Courier New", 9),
                 bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w", padx=14)

        self.log_box = scrolledtext.ScrolledText(
            left, font=("Courier New", 9),
            bg=BG_DEEP, fg=TEXT_MAIN,
            relief=tk.FLAT, bd=0,
            state=tk.DISABLED, height=10,
            wrap=tk.WORD)
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4,12))

        #  Right panel 
        right = tk.Frame(body, bg=BG_PANEL, width=280)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(4,10), pady=10)
        right.pack_propagate(False)

        # Leaderboard
        tk.Label(right, text="🏆  TOP ESCAPES",
                 font=("Courier New", 10, "bold"),
                 bg=BG_PANEL, fg=GOLD).pack(pady=(14,4))
        tk.Frame(right, bg=GOLD, height=1).pack(fill=tk.X, padx=10)

        self.leader_box = tk.Text(right, font=("Courier New", 10),
                                  bg=BG_PANEL, fg=TEXT_MAIN,
                                  relief=tk.FLAT, bd=0,
                                  state=tk.DISABLED, height=8)
        self.leader_box.pack(fill=tk.X, padx=10, pady=8)

        # AI players
        tk.Label(right, text="🤙  SURFERS",
                 font=("Courier New", 10, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(pady=(8,4))
        tk.Frame(right, bg=ACCENT2, height=1).pack(fill=tk.X, padx=10)

        self.ai_box = tk.Text(right, font=("Courier New", 9),
                              bg=BG_DEEP, fg=TEXT_MAIN,
                              relief=tk.FLAT, bd=0,
                              state=tk.DISABLED, height=14)
        self.ai_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Stats
        tk.Frame(right, bg=ACCENT2, height=1).pack(fill=tk.X, padx=10)
        self.stats_lbl = tk.Label(right, text="Rounds: 0  |  Best: —",
                                  font=("Courier New", 8),
                                  bg=BG_PANEL, fg=TEXT_DIM)
        self.stats_lbl.pack(pady=6)

        # Footer
        tk.Frame(self.root, bg=ACCENT2, height=1).pack(fill=tk.X)
        tk.Label(self.root,
                 text="Tsunami Escape  ·  Bet smart. Escape faster.",
                 font=("Courier New", 8),
                 bg=BG_DEEP, fg=TEXT_DIM).pack(pady=4)

        # Init stats
        self.rounds_played = 0
        self.best_mult     = 0.0
        self._refresh_leaderboard()

    #  Wave animation 
    def _animate_wave(self):
        import math
        c = self.wave_canvas
        c.delete("all")
        w = c.winfo_width() or 860
        h = 160
        self.wave_phase += 0.08

        # Intensity scales with multiplier when running
        intensity = min(self.multiplier / 2, 4) if self.running else 1.0
        amp   = 20 + intensity * 14
        freq  = 0.018 + intensity * 0.004
        speed = self.wave_phase

        pts = [0, h]
        for x in range(0, w + 4, 4):
            y = (h // 2
                 + amp * math.sin(freq * x + speed)
                 + (amp * 0.4) * math.sin(freq * 2 * x - speed * 1.3))
            pts += [x, y]
        pts += [w, h]

        # Colour shifts red as multiplier climbs
        if not self.running:
            fill, outline = "#003355", ACCENT2
        elif self.multiplier < 2:
            fill, outline = "#004477", ACCENT
        elif self.multiplier < 3.5:
            fill, outline = "#554400", GOLD
        else:
            fill, outline = "#550000", DANGER

        c.create_polygon(pts, fill=fill, outline=outline, width=2, smooth=True)

        # Surfer emoji on wave
        if self.running:
            sx = (w // 2) + int(20 * math.sin(speed * 0.7))
            sy = (h // 2
                  + amp * math.sin(freq * sx + speed)
                  + (amp * 0.4) * math.sin(freq * 2 * sx - speed * 1.3)) - 18
            c.create_text(sx, sy, text="🏄", font=("Segoe UI Emoji", 18))

        self.root.after(50, self._animate_wave)

    #  Helpers 
    def _quick_bet(self, amt: int):
        self.bet_entry.delete(0, tk.END)
        self.bet_entry.insert(0, str(amt))

    def log(self, msg: str, color: str = TEXT_MAIN):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.config(state=tk.DISABLED)
        self.log_box.see(tk.END)

    def _update_balance(self):
        self.balance_lbl.config(text=f"Balance: R{self.balance:,.2f}")

    def _refresh_leaderboard(self):
        self.leader_box.config(state=tk.NORMAL)
        self.leader_box.delete("1.0", tk.END)
        if not self.leaderboard:
            self.leader_box.insert(tk.END, "  No escapes yet...\n")
        medals = ["🥇", "🥈", "🥉", "4.", "5."]
        for i, (mult, win) in enumerate(self.leaderboard):
            self.leader_box.insert(tk.END,
                f"  {medals[i]}  x{mult}  →  R{win:,.2f}\n")
        self.leader_box.config(state=tk.DISABLED)

    def _refresh_ai(self):
        self.ai_box.config(state=tk.NORMAL)
        self.ai_box.delete("1.0", tk.END)
        for p in self.players:
            status = "🟢 riding" if p["active"] else f"✅ out at x{p['cash_out']}"
            self.ai_box.insert(tk.END, f"  {p['name']}: {status}\n")
        self.ai_box.config(state=tk.DISABLED)

    def _update_stats(self):
        best = f"x{self.best_mult}" if self.best_mult else "—"
        self.stats_lbl.config(
            text=f"Rounds: {self.rounds_played}  |  Best: {best}")

    #  Round logic 
    def start_round(self):
        try:
            bet_val = float(self.bet_entry.get())
        except ValueError:
            self.log("⚠ Enter a valid bet amount.")
            return

        if bet_val <= 0 or bet_val > self.balance:
            self.log("⚠ Invalid bet — check your balance.")
            return

        self.bet        = bet_val
        self.balance   -= self.bet
        self.multiplier = 1.0
        self.running    = True
        self.players    = simulate_ai_players()
        self.skill_active = False
        self.rounds_played += 1

        self._update_balance()
        self._refresh_ai()
        self.mult_lbl.config(text="x1.00", fg=ACCENT)
        self.status_lbl.config(text="🌊 Wave rising — escape before it crashes!", fg=TEXT_MAIN)
        self.start_btn.config(state=tk.DISABLED)
        self.cash_btn.config(state=tk.NORMAL)
        self.log(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self.log(f"▶ Round started — Bet: R{self.bet:,.2f}")

        threading.Thread(target=self._round_loop, daemon=True).start()

    def _round_loop(self):
        while self.running:
            time.sleep(0.8)
            self.multiplier = round(
                self.multiplier + random.uniform(0.08, 0.45), 2)

            # Skill event
            if not self.skill_active and random.random() < 0.12:
                self.root.after(0, self._trigger_skill)

            # AI cash-outs
            for p in self.players:
                if p["active"] and self.multiplier >= p["cash_out"]:
                    p["active"] = False
                    self.root.after(0, lambda p=p: (
                        self.log(f"  {p['name']} escaped at x{p['cash_out']} — {p['msg']}"),
                        self._refresh_ai()
                    ))

            # Crash check
            crash_chance = get_crash_chance(self.multiplier)
            if self.skill_active:
                crash_chance *= 0.5

            crashed = random.random() < crash_chance

            self.root.after(0, lambda m=self.multiplier, c=crashed: self._tick(m, c))

            if crashed:
                break

    def _tick(self, mult: float, crashed: bool):
        color = (ACCENT if mult < 2
                 else GOLD if mult < 3.5
                 else DANGER)
        self.mult_lbl.config(text=f"x{mult:.2f}", fg=color)

        if crashed:
            self.running = False
            self.skill_active = False
            if self.skill_btn:
                try: self.skill_btn.destroy()
                except: pass
            self.mult_lbl.config(fg=DANGER)
            self.status_lbl.config(text="💥 The tsunami crashed! You lost your bet.", fg=DANGER)
            self.log(f"💥 CRASHED at x{mult:.2f} — Lost R{self.bet:,.2f}")
            self.start_btn.config(state=tk.NORMAL)
            self.cash_btn.config(state=tk.DISABLED)
            self._update_stats()

    def cash_out(self):
        if not self.running:
            return
        self.running = False
        winnings = round(self.bet * self.multiplier, 2)
        self.balance += winnings
        profit = round(winnings - self.bet, 2)

        self.log(f"🏄 ESCAPED at x{self.multiplier:.2f} — Won R{winnings:,.2f}  (profit: R{profit:,.2f})")
        self.status_lbl.config(
            text=f"🏄 Escaped at x{self.multiplier:.2f} — Won R{winnings:,.2f}!",
            fg=GREEN)
        self.mult_lbl.config(fg=GREEN)
        self._update_balance()

        # Leaderboard
        self.leaderboard.append((round(self.multiplier, 2), winnings))
        self.leaderboard.sort(key=lambda x: x[0], reverse=True)
        self.leaderboard = self.leaderboard[:5]
        self._refresh_leaderboard()

        if self.multiplier > self.best_mult:
            self.best_mult = round(self.multiplier, 2)

        self.start_btn.config(state=tk.NORMAL)
        self.cash_btn.config(state=tk.DISABLED)
        self._update_stats()

        if self.balance <= 0:
            self.log("❌ Out of money! Game over.")
            self.start_btn.config(state=tk.DISABLED)

    #  Skill event 
    def _trigger_skill(self):
        if not self.running:
            return
        self.skill_active = True
        self.log("⚡ SKILL EVENT — Click fast to stabilize the wave!")
        self.skill_btn = tk.Button(
            self.skill_frame,
            text="⚡ STABILIZE THE WAVE — CLICK NOW!",
            font=("Courier New", 10, "bold"),
            bg=DANGER, fg=TEXT_MAIN,
            activebackground=GOLD,
            relief=tk.FLAT, bd=0, cursor="hand2",
            pady=6,
            command=self._activate_skill)
        self.skill_btn.pack(fill=tk.X)
        self.root.after(2000, self._expire_skill)

    def _activate_skill(self):
        self.skill_active = False
        self.log("✅ Wave stabilized! Crash chance halved.")
        if self.skill_btn:
            self.skill_btn.destroy()
            self.skill_btn = None

    def _expire_skill(self):
        if self.skill_btn:
            self.skill_active = False
            self.log("❌ Missed the skill window!")
            self.skill_btn.destroy()
            self.skill_btn = None

#  Run 
if __name__ == "__main__":
    root = tk.Tk()
    TsunamiApp(root)
    root.mainloop()