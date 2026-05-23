"""
============================================================================
  NeuroSim — EEG Brain State Recognition Game
============================================================================

  ====================  RUN THIS FILE TO START  =========================

  Command:
      python main.py

  Requirements:
      Python 3.9 or newer
      numpy   (pip install numpy)
      pygame  (pip install pygame)

  Or install everything at once:
      pip install -r requirements.txt

  ----------------------------------------------------------------------
  IMPORTANT — for the tutor:
  ----------------------------------------------------------------------
  This program uses NON-BUILT-IN libraries (numpy, pygame) and opens a
  GRAPHICAL WINDOW. It therefore CANNOT run inside Ed's web environment.
  Please run it from a normal terminal on your laptop instead.

  Author: Lin-Fan (Ada) Gong
  Unit:   COMP9001 — Final Project (2026 S1)
============================================================================
"""

from gui_game import NeuroSimGame


def main():
    NeuroSimGame().run()


if __name__ == "__main__":
    main()
