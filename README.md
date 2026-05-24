# NeuroSim — Mind Reader: Brain Wave Challenge

An educational simulation game that generates realistic EEG (brain wave) signals and challenges the player to identify the underlying mental state. A rule-based AI plays alongside you — can you read brain waves better than a machine?

Final project for COMP9001 at the University of Sydney.

## About

Real human brains produce electrical activity in characteristic frequency bands. NeuroSim simulates these signals, displays them on a live scrolling monitor similar to clinical EEG equipment, and turns them into a guessing game with five brain states:

| Band  | Frequency  | Mental state          |
|-------|------------|-----------------------|
| Delta | 0.5–4 Hz   | Deep sleep            |
| Theta | 4–8 Hz     | Drowsy / meditative   |
| Alpha | 8–13 Hz    | Relaxed               |
| Beta  | 13–30 Hz   | Focused               |
| Gamma | 30–50 Hz   | High cognition        |

Each round, the program generates a noisy four-channel signal in one of these bands, renders it as a live scrolling waveform plus a power spectrum, and asks the player to guess. A rule-based AI plays at the same time, so every round is a human-vs-AI showdown.

## How to run

Requires Python 3.9+, `numpy`, and `pygame`. Opens a graphical window, so it **will not run inside Ed** — please use PyCharm or a normal terminal.

**PyCharm:** open the `neurosim` folder, accept the venv prompt, install `requirements.txt`, then right-click `main.py` → Run.

**Terminal:**
```bash
cd neurosim
pip install -r requirements.txt
python main.py
```

## Controls

Enter your name, pick a difficulty and number of rounds, then click one of the five colored buttons (or press 1–5) to guess. Press ESC to return to the main menu.
