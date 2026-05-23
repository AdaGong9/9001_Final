# NeuroSim — Mind Reader: Brain Wave Challenge

An educational simulation game that generates realistic EEG (brain wave) signals and challenges the player to identify the underlying mental state. A rule-based AI plays alongside you — can you read brain waves better than a machine?

Built as the final project for COMP9001 (Introduction to Programming) at the University of Sydney.

---

## About

Real human brains produce electrical activity in characteristic frequency bands. NeuroSim simulates these signals based on actual neuroscience, displays them on a live scrolling monitor similar to clinical EEG equipment, and turns them into a guessing game.

Five brain states are simulated:

| Band | Frequency | Mental state |
|------|-----------|--------------|
| Delta | 0.5–4 Hz | Deep sleep |
| Theta | 4–8 Hz | Drowsy / meditative |
| Alpha | 8–13 Hz | Relaxed |
| Beta | 13–30 Hz | Focused |
| Gamma | 30–50 Hz | High cognition |

Each round, the program generates a noisy four-channel EEG signal in one of these bands, renders it as a live scrolling waveform plus a real-time power spectrum, and asks the player to guess which state it represents. A simple rule-based classifier — based on band power — plays at the same time, so every round is a human-vs-AI showdown.

---

## Features

- Real-time scrolling EEG animation rendered directly with Pygame (no matplotlib)
- Four-channel signal generation using NumPy, with FFT-based power spectrum analysis
- Five brain states based on real neuroscience frequency bands
- Three difficulty levels controlling signal noise
- Rule-based AI classifier that competes against the player
- Custom text input widget for entering player names
- JSON-based persistent leaderboard
- Custom exception hierarchy for robust input handling
- Modular architecture (9 Python files)
- Full unit-test suite with 11 passing tests

---

## Run

Requires Python 3.9 or newer, plus `numpy` and `pygame`.

```bash
cd neurosim
pip install -r requirements.txt
python3 main.py
```

For step-by-step PyCharm instructions, see [`neurosim/README.txt`](neurosim/README.txt).

### Gameplay

1. Enter your name on the welcome screen.
2. Choose a difficulty (easy / medium / hard) and a number of rounds (3 / 5 / 10).
3. Watch the live scrolling EEG trace and the power spectrum below it.
4. Click one of the five colored buttons — or press 1–5 on the keyboard — to submit your guess.
5. After each guess, the correct frequency band is highlighted on the spectrum so you can verify the answer.
6. Press ESC at any time to return to the main menu.

---

## Tests

```bash
cd neurosim
python -m unittest test_neurosim.py -v
```

All 11 tests should pass. The suite covers signal generation, classifier accuracy, invalid-input handling, and JSON leaderboard round-trips.

---

## Project structure

```
neurosim/
├── main.py              # Entry point — run this file
├── gui_game.py          # Pygame screen state machine & rendering
├── plot_widgets.py      # Custom waveform & spectrum drawing
├── ui.py                # Colors, fonts, Button, TextInput widgets
├── eeg_generator.py     # EEG signal generation (NumPy + FFT)
├── data_manager.py      # JSON read/write for the leaderboard
├── exceptions.py        # Custom exception classes
├── test_neurosim.py     # Unit-test suite (unittest)
├── requirements.txt     # pip dependency list
└── README.txt           # Detailed run instructions for tutors
```

---

## Tech stack

- **Python 3.9+**
- **Pygame** — windowing, event loop, custom rendering
- **NumPy** — multi-channel signal matrices, FFT, vectorized operations
- **unittest** — standard-library testing framework
- **json** — leaderboard persistence

No matplotlib, no audio, no networking.

---

