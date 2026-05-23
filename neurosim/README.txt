============================================================
  NeuroSim — EEG Brain State Recognition Game
  COMP9001 Final Project
  Author: Lin-Fan (Ada) Gong
============================================================


WHAT IT IS
----------
NeuroSim is a pygame-based educational game that simulates EEG (brain
wave) signals and challenges the player to identify which mental state
each signal represents. Real human brains produce electrical activity
in characteristic frequency bands:

    Delta  (0.5-4 Hz)  - Deep sleep
    Theta  (4-8 Hz)    - Drowsy / meditative
    Alpha  (8-13 Hz)   - Relaxed
    Beta   (13-30 Hz)  - Focused
    Gamma  (30-50 Hz)  - High cognition

The program generates realistic-looking multi-channel signals, shows
the time-domain waveform as a live scrolling trace (like a clinical
EEG monitor) and the power spectrum at the bottom, then asks you to
choose the correct state. A simple rule-based "AI" plays alongside
you, so each round is a human-vs-AI showdown.


============================================================
  ENTRY POINT
============================================================

    >>>  Run main.py  <<<

All other .py files in this folder are imported by main.py.


============================================================
  HOW TO RUN
============================================================

REQUIREMENTS
------------
  - Python 3.10 or newer
  - numpy   (non built-in)
  - pygame  (non built-in)


OPTION A — PyCharm (easiest)
----------------------------
  1. Open the neurosim folder in PyCharm (File > Open).
  2. PyCharm will offer to create a virtual environment — accept it.
  3. Open requirements.txt; PyCharm will show an "Install requirements"
     banner at the top of the file. Click it.
  4. Right-click main.py > Run 'main'.


OPTION B — Terminal
-------------------
  1. cd into the neurosim folder.

  2. (Recommended) Create a virtual environment so the install does
     not touch your system Python:

        python -m venv venv
        source venv/bin/activate          # macOS / Linux
        venv\Scripts\activate             # Windows

  3. Install dependencies:

        pip install -r requirements.txt

  4. Run the program:

        python main.py


GAMEPLAY
--------
  1. Enter your name on the welcome screen, or press Enter to use
     the default.
  2. Choose a difficulty (easy / medium / hard) and a number of
     rounds (3 / 5 / 10).
  3. During a round you'll see a LIVE scrolling EEG trace at the top
     and a power spectrum at the bottom. Click one of the five
     colored buttons to submit your guess, or press 1-5 on the
     keyboard.
  4. After each guess, the correct frequency band is highlighted on
     the spectrum so you can verify the answer.
  5. Press ESC at any time to return to the main menu.


============================================================
  RUNNING THE TESTS
============================================================

The project includes a unit-test suite. To run it:

    python -m unittest test_neurosim.py -v

All 11 tests should pass.


============================================================
  IMPORTANT NOTE FOR TUTOR
============================================================

This program uses libraries OUTSIDE Python's built-in libraries:

    - numpy   (numerical arrays, FFT)
    - pygame  (graphics / GUI)

It also opens a GRAPHICAL WINDOW (pygame).

For these reasons, this program WILL NOT RUN INSIDE ED's web
environment. Please run it from a normal terminal or PyCharm
on your local machine (Windows / macOS / Linux all work fine).

No audio, no video, no networking is used.


============================================================
  FILE LAYOUT
============================================================

   main.py            <-- ENTRY POINT — run this file
   gui_game.py        Pygame screen state machine & rendering
   plot_widgets.py    Custom waveform + spectrum drawing
   ui.py              Colors, fonts, Button, TextInput widgets
   eeg_generator.py   EEG signal generation (NumPy + FFT)
   data_manager.py    JSON read/write for the leaderboard
   exceptions.py      Custom exception classes
   test_neurosim.py   Unit-test suite (unittest)
   requirements.txt   pip dependency list
   README.txt         This file
   data/              Created automatically; holds scores.json


============================================================
  ADVANCED TOPICS DEMONSTRATED
============================================================

   1. NumPy & multi-dimensional lists
        - 2D signal matrices (channels x samples)
        - FFT-based power spectral density
        - np.roll for seamless scrolling animation
      See: eeg_generator.py, plot_widgets.py

   2. File Input / Output
        - JSON read/write for score persistence and leaderboard
      See: data_manager.py

   3. More Flow Control
        - Custom exception class hierarchy
        - raise / try / except / continue / break
      See: exceptions.py, gui_game.py, ui.py

   4. Testing (unittest)
        - 11 unit tests covering signal shape, classifier accuracy,
          invalid-input handling, and JSON round-trips
      See: test_neurosim.py


============================================================
