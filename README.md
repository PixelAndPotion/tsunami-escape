# Tsunami Escape 🌊

A crash-style betting game built in pure Python with Tkinter. Ride the wave, cash out before it crashes, and beat your own multiplier record.



## Features

| Feature | Detail |
|---|---|
| 🌊 Live wave animation | Canvas wave that intensifies as multiplier climbs |
| 💰 Betting system | Custom bet or quick-select R100 / R500 / R1000 / R5000 |
| 🤖 AI surfers | 5 AI players with different risk strategies |
| ⚡ Skill events | Click-fast mechanic that halves crash probability |
| 🏆 Leaderboard | Top 5 personal escapes tracked per session |
| 🎨 Dynamic colours | Multiplier label and wave shift green → gold → red |



## Stack

- Python 3.10+
- Tkinter — GUI and canvas animation
- Threading — non-blocking game loop
- No external packages



## How to run

```bash
python tsunami_escape.py
```



## How to play

1. Enter a bet amount or click a quick-bet button
2. Click **START ROUND** — the wave begins rising
3. Click **ESCAPE NOW** before the tsunami crashes
4. If a ⚡ skill event appears, click it fast to reduce crash chance
5. Cash out multiplier is added to your leaderboard if it's a top 5

