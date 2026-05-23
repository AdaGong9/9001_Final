"""
gui_game.py — Pygame front-end for NeuroSim.

This module is imported by main.py — do NOT run it directly.
Run `python main.py` instead.

Implements a screen-based state machine:
    MENU -> NAME_ENTRY -> SETUP -> GAME -> RESULT -> GAME_OVER
                                                  -> LEADERBOARD
                                                  -> ABOUT
"""

import random
import sys
from typing import List, Optional

import numpy as np
import pygame

from eeg_generator import EEGGenerator, BRAIN_STATES, classify_by_band_power
from data_manager import save_score, get_leaderboard
from plot_widgets import draw_waveform_panel, draw_spectrum_panel
from ui import Colors, Fonts, Button, TextInput


# Window dimensions
WIDTH, HEIGHT = 1000, 720
FPS = 60

# Screen states
SCREEN_MENU        = "menu"
SCREEN_NAME_ENTRY  = "name_entry"
SCREEN_SETUP       = "setup"
SCREEN_GAME        = "game"
SCREEN_RESULT      = "result"
SCREEN_GAME_OVER   = "game_over"
SCREEN_LEADERBOARD = "leaderboard"
SCREEN_ABOUT       = "about"


# ---------------------------------------------------------------------------
# Helper: render a centered text line
# ---------------------------------------------------------------------------
def draw_text(surface, text: str, font, color, center=None, topleft=None):
    s = font.render(text, True, color)
    r = s.get_rect()
    if center is not None:
        r.center = center
    elif topleft is not None:
        r.topleft = topleft
    surface.blit(s, r)


# ---------------------------------------------------------------------------
# Main game class
# ---------------------------------------------------------------------------
class NeuroSimGame:
    def __init__(self):
        pygame.init()
        Fonts.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("NeuroSim — EEG Brain State Game")
        self.clock = pygame.time.Clock()

        # Game state
        self.state = SCREEN_MENU
        self.player_name = ""
        self.difficulty = "medium"
        self.n_rounds = 5
        self.current_round = 0
        self.user_score = 0
        self.ai_score = 0

        # Current round data
        self.generator = EEGGenerator(sampling_rate=250, duration=4.0,
                                      n_channels=4)
        self.current_signal: Optional[np.ndarray] = None
        self.true_state: str = ""
        self.user_guess: Optional[str] = None
        self.ai_guess: str = ""

        # Animation: scroll offset for the live EEG display.
        # Advances by `scroll_speed` samples per frame while in SCREEN_GAME.
        self.scroll_offset = 0
        self.scroll_speed = 4

        # Text input field (rebuilt when entering the name screen)
        self.name_input: Optional[TextInput] = None

        # Buttons (rebuilt per screen)
        self.buttons: List[Button] = []
        self._build_menu()

    # -----------------------------------------------------------------
    # Screen builders
    # -----------------------------------------------------------------
    def _build_menu(self):
        cx = WIDTH // 2
        self.buttons = [
            Button(cx - 140, 280, 280, 55, "Play",
                   hover_color=Colors.SUCCESS, action_value="play"),
            Button(cx - 140, 350, 280, 55, "Leaderboard",
                   hover_color=Colors.WARNING, action_value="leaderboard"),
            Button(cx - 140, 420, 280, 55, "About",
                   hover_color=Colors.ACCENT, action_value="about"),
            Button(cx - 140, 490, 280, 55, "Quit",
                   hover_color=Colors.ERROR, action_value="quit"),
        ]

    def _build_name_entry(self):
        cx = WIDTH // 2
        # Input field (centered)
        self.name_input = TextInput(
            x=cx - 200, y=320, w=400, h=60,
            placeholder="Type your name...",
            max_length=18,
            initial=self.player_name,
        )
        self.buttons = [
            Button(cx - 200, 440, 180, 55, "Back",
                   hover_color=Colors.ERROR, action_value="back"),
            Button(cx + 20, 440, 180, 55, "Continue",
                   hover_color=Colors.SUCCESS, action_value="name_done"),
        ]

    def _build_setup(self):
        cx = WIDTH // 2
        self.buttons = []
        # Difficulty buttons
        diff_y = 280
        diff_colors = {"easy": Colors.SUCCESS,
                       "medium": Colors.WARNING,
                       "hard": Colors.ERROR}
        for i, diff in enumerate(["easy", "medium", "hard"]):
            btn = Button(cx - 240 + i * 160, diff_y, 140, 50,
                         diff.upper(),
                         hover_color=diff_colors[diff],
                         action_value=("difficulty", diff))
            self.buttons.append(btn)

        # Round count buttons
        round_y = 410
        for i, n in enumerate([3, 5, 10]):
            btn = Button(cx - 240 + i * 160, round_y, 140, 50,
                         f"{n} rounds",
                         hover_color=Colors.ACCENT,
                         action_value=("rounds", n))
            self.buttons.append(btn)

        # Start / back
        self.buttons.append(
            Button(cx - 200, 540, 180, 55, "Back",
                   hover_color=Colors.ERROR, action_value="back"))
        self.buttons.append(
            Button(cx + 20, 540, 180, 55, "Start",
                   hover_color=Colors.SUCCESS, action_value="start"))

    def _build_game_buttons(self):
        """Buttons for the 5 brain-state guesses."""
        self.buttons = []
        states = list(BRAIN_STATES.keys())
        btn_w = 170
        btn_h = 60
        total_w = btn_w * len(states) + 15 * (len(states) - 1)
        start_x = (WIDTH - total_w) // 2
        y = HEIGHT - 90
        for i, state in enumerate(states):
            color = Colors.STATES[state]
            x = start_x + i * (btn_w + 15)
            btn = Button(x, y, btn_w, btn_h, state.upper(),
                         hover_color=color, action_value=("guess", state),
                         font=Fonts.heading)
            self.buttons.append(btn)

    def _build_result_buttons(self):
        cx = WIDTH // 2
        is_last = self.current_round >= self.n_rounds
        label = "Finish" if is_last else "Next Round"
        self.buttons = [
            Button(cx - 120, HEIGHT - 80, 240, 50, label,
                   hover_color=Colors.SUCCESS, action_value="next"),
        ]

    def _build_game_over_buttons(self):
        cx = WIDTH // 2
        self.buttons = [
            Button(cx - 250, HEIGHT - 100, 220, 55, "Leaderboard",
                   hover_color=Colors.WARNING, action_value="leaderboard"),
            Button(cx - 20,  HEIGHT - 100, 220, 55, "Play Again",
                   hover_color=Colors.ACCENT, action_value="play_again"),
            Button(cx + 210, HEIGHT - 100, 220, 55, "Main Menu",
                   hover_color=Colors.SUCCESS, action_value="menu"),
        ]

    def _build_back_button(self):
        self.buttons = [
            Button(40, HEIGHT - 80, 160, 50, "Back",
                   hover_color=Colors.ERROR, action_value="menu"),
        ]

    # -----------------------------------------------------------------
    # Round logic
    # -----------------------------------------------------------------
    def start_new_round(self):
        self.current_round += 1
        noise = {"easy": 0.2, "medium": 0.5, "hard": 0.9}[self.difficulty]
        self.true_state = random.choice(list(BRAIN_STATES.keys()))
        self.current_signal = self.generator.generate(self.true_state,
                                                      noise_level=noise)
        self.ai_guess = classify_by_band_power(self.current_signal[0],
                                               self.generator)
        self.user_guess = None
        self.scroll_offset = 0  # reset animation for the new signal
        self._build_game_buttons()

    def submit_guess(self, guess: str):
        self.user_guess = guess
        if guess == self.true_state:
            self.user_score += 1
        if self.ai_guess == self.true_state:
            self.ai_score += 1
        self.state = SCREEN_RESULT
        self._build_result_buttons()

    def finish_game(self):
        save_score(self.player_name, self.user_score, self.n_rounds,
                   ai_score=self.ai_score)
        self.state = SCREEN_GAME_OVER
        self._build_game_over_buttons()

    # -----------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------
    def handle_button_action(self, action):
        """Dispatch a button's action_value to the right handler."""
        if action == "quit":
            self.quit()
        elif action == "play":
            self._build_name_entry()
            self.state = SCREEN_NAME_ENTRY
        elif action == "name_done":
            # Strip whitespace; fall back to a default if empty
            name = self.name_input.text.strip() if self.name_input else ""
            self.player_name = name or "Anonymous"
            self._build_setup()
            self.state = SCREEN_SETUP
        elif action == "leaderboard":
            self._build_back_button()
            self.state = SCREEN_LEADERBOARD
        elif action == "about":
            self._build_back_button()
            self.state = SCREEN_ABOUT
        elif action == "back" or action == "menu":
            self._build_menu()
            self.state = SCREEN_MENU
        elif action == "start":
            self.user_score = 0
            self.ai_score = 0
            self.current_round = 0
            self.start_new_round()
            self.state = SCREEN_GAME
        elif action == "next":
            if self.current_round >= self.n_rounds:
                self.finish_game()
            else:
                self.start_new_round()
                self.state = SCREEN_GAME
        elif action == "play_again":
            self._build_setup()
            self.state = SCREEN_SETUP
        elif isinstance(action, tuple):
            kind, value = action
            if kind == "difficulty":
                self.difficulty = value
            elif kind == "rounds":
                self.n_rounds = value
            elif kind == "guess":
                self.submit_guess(value)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == SCREEN_MENU:
                        self.quit()
                    else:
                        self._build_menu()
                        self.state = SCREEN_MENU
                    continue

                # On the name-entry screen, all other keystrokes feed the
                # text input. Enter behaves the same as "Continue".
                if self.state == SCREEN_NAME_ENTRY and self.name_input:
                    if self.name_input.handle_event(event):
                        self.handle_button_action("name_done")
                    continue

                # Keyboard shortcuts during a round: 1-5 to guess
                if self.state == SCREEN_GAME and self.user_guess is None:
                    states = list(BRAIN_STATES.keys())
                    if pygame.K_1 <= event.key <= pygame.K_5:
                        idx = event.key - pygame.K_1
                        if idx < len(states):
                            self.submit_guess(states[idx])

            for btn in self.buttons:
                if btn.clicked(event):
                    self.handle_button_action(btn.action_value)
                    return  # state changed; rebuild buttons next frame

        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)

    # -----------------------------------------------------------------
    # Drawing
    # -----------------------------------------------------------------
    def draw_menu(self):
        self.screen.fill(Colors.BG)
        draw_text(self.screen, "NeuroSim", Fonts.title,
                  Colors.ACCENT, center=(WIDTH // 2, 130))
        draw_text(self.screen, "EEG Brain State Recognition Game",
                  Fonts.heading, Colors.TEXT, center=(WIDTH // 2, 180))
        draw_text(self.screen, "Can you read brain waves better than an AI?",
                  Fonts.body, Colors.TEXT_DIM, center=(WIDTH // 2, 215))
        for b in self.buttons:
            b.draw(self.screen)
        draw_text(self.screen, "Press ESC at any time to return to the menu",
                  Fonts.small, Colors.TEXT_DIM,
                  center=(WIDTH // 2, HEIGHT - 30))

    def draw_name_entry(self):
        self.screen.fill(Colors.BG)
        draw_text(self.screen, "Who's playing?", Fonts.title,
                  Colors.ACCENT, center=(WIDTH // 2, 180))
        draw_text(self.screen,
                  "Your name will be saved to the leaderboard.",
                  Fonts.body, Colors.TEXT_DIM,
                  center=(WIDTH // 2, 240))
        draw_text(self.screen, "Press Enter to continue",
                  Fonts.small, Colors.TEXT_DIM,
                  center=(WIDTH // 2, 405))

        if self.name_input is not None:
            self.name_input.draw(self.screen)

        for b in self.buttons:
            b.draw(self.screen)

    def draw_setup(self):
        self.screen.fill(Colors.BG)
        draw_text(self.screen, "Game Setup", Fonts.title,
                  Colors.ACCENT, center=(WIDTH // 2, 130))

        draw_text(self.screen, "Difficulty", Fonts.heading,
                  Colors.TEXT, center=(WIDTH // 2, 250))
        # Highlight current selection
        for b in self.buttons:
            if (isinstance(b.action_value, tuple)
                    and b.action_value[0] == "difficulty"
                    and b.action_value[1] == self.difficulty):
                pygame.draw.rect(self.screen, Colors.ACCENT,
                                 b.rect.inflate(8, 8),
                                 width=3, border_radius=10)
            if (isinstance(b.action_value, tuple)
                    and b.action_value[0] == "rounds"
                    and b.action_value[1] == self.n_rounds):
                pygame.draw.rect(self.screen, Colors.ACCENT,
                                 b.rect.inflate(8, 8),
                                 width=3, border_radius=10)

        draw_text(self.screen, "Number of rounds", Fonts.heading,
                  Colors.TEXT, center=(WIDTH // 2, 380))

        for b in self.buttons:
            b.draw(self.screen)

    def draw_game(self):
        self.screen.fill(Colors.BG)

        # Header bar
        header = f"Round {self.current_round} / {self.n_rounds}"
        draw_text(self.screen, header, Fonts.heading,
                  Colors.ACCENT, topleft=(20, 15))
        # Player name + score on the right
        right_text = f"{self.player_name}: {self.user_score}    AI: {self.ai_score}"
        draw_text(self.screen, right_text, Fonts.heading,
                  Colors.TEXT, topleft=(WIDTH - 360, 15))

        # Show ~2 s of signal in the scrolling window
        window_samples = int(self.generator.fs * 2.0)

        # Waveform panel (animated)
        wave_rect = pygame.Rect(20, 60, WIDTH - 40, 320)
        draw_waveform_panel(self.screen, wave_rect, self.current_signal,
                            duration=2.0,
                            scroll_offset=self.scroll_offset,
                            window_samples=window_samples,
                            animated=True)

        # Spectrum panel (static -- PSD doesn't change moment to moment)
        spec_rect = pygame.Rect(20, 395, WIDTH - 40, 195)
        freqs, power = self.generator.compute_psd(self.current_signal[0])
        draw_spectrum_panel(self.screen, spec_rect, freqs, power)

        # Prompt
        draw_text(self.screen, "Which brain state is this?", Fonts.heading,
                  Colors.TEXT, center=(WIDTH // 2, 615))

        for b in self.buttons:
            b.draw(self.screen)

    def draw_result(self):
        self.screen.fill(Colors.BG)
        correct = self.user_guess == self.true_state
        ai_correct = self.ai_guess == self.true_state

        # Header
        result_text = "Correct!" if correct else "Not quite."
        result_color = Colors.SUCCESS if correct else Colors.ERROR
        draw_text(self.screen, result_text, Fonts.title,
                  result_color, center=(WIDTH // 2, 50))

        # Frozen waveform showing what the player just saw
        window_samples = int(self.generator.fs * 2.0)
        wave_rect = pygame.Rect(20, 100, WIDTH - 40, 280)
        draw_waveform_panel(self.screen, wave_rect, self.current_signal,
                            duration=2.0,
                            scroll_offset=self.scroll_offset,
                            window_samples=window_samples,
                            animated=False)

        # Spectrum with answer band revealed
        spec_rect = pygame.Rect(20, 395, WIDTH - 40, 175)
        freqs, power = self.generator.compute_psd(self.current_signal[0])
        draw_spectrum_panel(self.screen, spec_rect, freqs, power,
                            reveal_state=self.true_state)

        # Summary lines
        y = 590
        info = BRAIN_STATES[self.true_state]
        draw_text(self.screen,
                  f"True state: {self.true_state.upper()} "
                  f"({info['band'][0]}-{info['band'][1]} Hz) — {info['label']}",
                  Fonts.body, Colors.TEXT, center=(WIDTH // 2, y))
        you_color = Colors.SUCCESS if correct else Colors.ERROR
        ai_color  = Colors.SUCCESS if ai_correct else Colors.ERROR
        draw_text(self.screen, f"You: {self.user_guess.upper()}",
                  Fonts.body, you_color, center=(WIDTH // 2 - 100, y + 28))
        draw_text(self.screen, f"AI:  {self.ai_guess.upper()}",
                  Fonts.body, ai_color, center=(WIDTH // 2 + 100, y + 28))

        for b in self.buttons:
            b.draw(self.screen)

    def draw_game_over(self):
        self.screen.fill(Colors.BG)
        draw_text(self.screen, "Game Over", Fonts.title,
                  Colors.ACCENT, center=(WIDTH // 2, 100))

        acc = self.user_score / max(self.n_rounds, 1)
        ai_acc = self.ai_score / max(self.n_rounds, 1)

        # Comparison verdict
        if self.user_score > self.ai_score:
            verdict = "You beat the AI!"
            verdict_color = Colors.SUCCESS
        elif self.user_score < self.ai_score:
            verdict = "The AI got more this time."
            verdict_color = Colors.WARNING
        else:
            verdict = "It's a tie!"
            verdict_color = Colors.ACCENT

        draw_text(self.screen, verdict, Fonts.heading,
                  verdict_color, center=(WIDTH // 2, 180))

        # Score boxes
        box_w, box_h = 280, 180
        you_box = pygame.Rect(WIDTH // 2 - box_w - 30, 240, box_w, box_h)
        ai_box  = pygame.Rect(WIDTH // 2 + 30, 240, box_w, box_h)
        pygame.draw.rect(self.screen, Colors.PANEL, you_box, border_radius=10)
        pygame.draw.rect(self.screen, Colors.PANEL, ai_box, border_radius=10)

        draw_text(self.screen, "You", Fonts.heading,
                  Colors.SUCCESS, center=you_box.center[:1] + (you_box.y + 30,))
        draw_text(self.screen, f"{self.user_score} / {self.n_rounds}",
                  Fonts.title, Colors.TEXT,
                  center=(you_box.centerx, you_box.y + 90))
        draw_text(self.screen, f"{acc:.0%} accuracy", Fonts.body,
                  Colors.TEXT_DIM,
                  center=(you_box.centerx, you_box.y + 140))

        draw_text(self.screen, "AI", Fonts.heading,
                  Colors.WARNING, center=(ai_box.centerx, ai_box.y + 30))
        draw_text(self.screen, f"{self.ai_score} / {self.n_rounds}",
                  Fonts.title, Colors.TEXT,
                  center=(ai_box.centerx, ai_box.y + 90))
        draw_text(self.screen, f"{ai_acc:.0%} accuracy", Fonts.body,
                  Colors.TEXT_DIM,
                  center=(ai_box.centerx, ai_box.y + 140))

        for b in self.buttons:
            b.draw(self.screen)

    def draw_leaderboard(self):
        self.screen.fill(Colors.BG)
        draw_text(self.screen, "Leaderboard", Fonts.title,
                  Colors.WARNING, center=(WIDTH // 2, 80))
        draw_text(self.screen, "Top 10 by accuracy", Fonts.body,
                  Colors.TEXT_DIM, center=(WIDTH // 2, 120))

        records = get_leaderboard(10)
        if not records:
            draw_text(self.screen, "No scores yet -- play a round!",
                      Fonts.heading, Colors.TEXT_DIM,
                      center=(WIDTH // 2, HEIGHT // 2))
        else:
            # Header row
            y = 170
            draw_text(self.screen, "Rank", Fonts.heading,
                      Colors.ACCENT, topleft=(140, y))
            draw_text(self.screen, "Player", Fonts.heading,
                      Colors.ACCENT, topleft=(230, y))
            draw_text(self.screen, "Score", Fonts.heading,
                      Colors.ACCENT, topleft=(450, y))
            draw_text(self.screen, "Accuracy", Fonts.heading,
                      Colors.ACCENT, topleft=(580, y))
            draw_text(self.screen, "Date", Fonts.heading,
                      Colors.ACCENT, topleft=(740, y))
            y += 35
            for i, rec in enumerate(records, start=1):
                color = Colors.WARNING if i <= 3 else Colors.TEXT
                draw_text(self.screen, f"#{i}", Fonts.body, color,
                          topleft=(140, y))
                draw_text(self.screen, rec["player"][:18], Fonts.body, color,
                          topleft=(230, y))
                draw_text(self.screen,
                          f"{rec['score']}/{rec['total']}",
                          Fonts.body, color, topleft=(450, y))
                draw_text(self.screen, f"{rec['accuracy']:.0%}",
                          Fonts.body, color, topleft=(580, y))
                draw_text(self.screen, rec["date"], Fonts.small,
                          Colors.TEXT_DIM, topleft=(740, y + 3))
                y += 32

        for b in self.buttons:
            b.draw(self.screen)

    def draw_about(self):
        self.screen.fill(Colors.BG)
        draw_text(self.screen, "About NeuroSim", Fonts.title,
                  Colors.ACCENT, center=(WIDTH // 2, 70))

        intro = [
            "Real human brains produce electrical activity in different",
            "frequency bands depending on what we're doing. NeuroSim",
            "simulates these signals and challenges you to identify them.",
        ]
        for i, line in enumerate(intro):
            draw_text(self.screen, line, Fonts.body,
                      Colors.TEXT_DIM, center=(WIDTH // 2, 130 + i * 28))

        # State table
        y = 250
        for state, info in BRAIN_STATES.items():
            color = Colors.STATES[state]
            low, high = info["band"]
            # Color swatch
            pygame.draw.rect(self.screen, color,
                             (220, y, 20, 20), border_radius=4)
            draw_text(self.screen, state.upper(), Fonts.heading,
                      color, topleft=(260, y - 2))
            draw_text(self.screen, f"{low}-{high} Hz",
                      Fonts.body, Colors.TEXT, topleft=(380, y))
            draw_text(self.screen, info["label"],
                      Fonts.body, Colors.TEXT_DIM, topleft=(520, y))
            y += 40

        draw_text(self.screen,
                  "Tip: Watch the power spectrum -- the dominant band is the answer.",
                  Fonts.body, Colors.ACCENT,
                  center=(WIDTH // 2, y + 30))

        for b in self.buttons:
            b.draw(self.screen)

    # -----------------------------------------------------------------
    # Main loop
    # -----------------------------------------------------------------
    def run(self):
        while True:
            dt = self.clock.tick(FPS)  # ms since last frame

            self.handle_events()

            # Update per-frame animations
            if self.state == SCREEN_GAME and self.current_signal is not None:
                # Advance the scroll position; wrap around the signal length
                n_samples = self.current_signal.shape[1]
                self.scroll_offset = (self.scroll_offset + self.scroll_speed) \
                    % n_samples
            if self.state == SCREEN_NAME_ENTRY and self.name_input is not None:
                self.name_input.update(dt)

            # Render the current screen
            if self.state == SCREEN_MENU:
                self.draw_menu()
            elif self.state == SCREEN_NAME_ENTRY:
                self.draw_name_entry()
            elif self.state == SCREEN_SETUP:
                self.draw_setup()
            elif self.state == SCREEN_GAME:
                self.draw_game()
            elif self.state == SCREEN_RESULT:
                self.draw_result()
            elif self.state == SCREEN_GAME_OVER:
                self.draw_game_over()
            elif self.state == SCREEN_LEADERBOARD:
                self.draw_leaderboard()
            elif self.state == SCREEN_ABOUT:
                self.draw_about()

            pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit(0)
