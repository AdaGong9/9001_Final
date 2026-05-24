
import pygame
from typing import Tuple


# Colors
class Colors:
    BG          = (18, 22, 33)        # background
    PANEL       = (28, 34, 48)        # panels behind plots
    PANEL_LIGHT = (38, 46, 64)
    GRID        = (50, 58, 78)
    TEXT        = (235, 240, 250)
    TEXT_DIM    = (150, 160, 180)
    ACCENT      = (102, 217, 239)     # cyan
    SUCCESS     = (166, 226, 46)      # green
    ERROR       = (249, 38, 114)      # pink/red
    WARNING     = (253, 151, 31)      # orange

    # Per-channel waveform colors
    CHANNELS = [
        (102, 217, 239),   # cyan
        (166, 226, 46),    # green
        (253, 151, 31),    # orange
        (249, 38, 114),    # pink
    ]

    # Per-brain-state colors
    STATES = {
        "delta": (147, 112, 219),  # purple
        "theta": (102, 217, 239),  # cyan
        "alpha": (166, 226, 46),   # green
        "beta":  (253, 151, 31),   # orange
        "gamma": (249, 38, 114),   # pink
    }


# Fonts
class Fonts:
    title = None
    heading = None
    body = None
    small = None
    mono = None

    @classmethod
    def init(cls):
        cls.title   = pygame.font.SysFont("arial", 36, bold=True)
        cls.heading = pygame.font.SysFont("arial", 22, bold=True)
        cls.body    = pygame.font.SysFont("arial", 18)
        cls.small   = pygame.font.SysFont("arial", 14)
        cls.mono    = pygame.font.SysFont("couriernew", 16)


# Button widget
class Button:

    def __init__(self, x: int, y: int, w: int, h: int, label: str,
                 color: tuple = Colors.PANEL_LIGHT,
                 hover_color: tuple = Colors.ACCENT,
                 text_color: tuple = Colors.TEXT,
                 font=None, action_value=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font  # set in draw() if None
        self.action_value = action_value  # what this button "returns" when clicked
        self.hovered = False
        self.disabled = False

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos) and not self.disabled

    def draw(self, surface: pygame.Surface) -> None:
        color = self.hover_color if self.hovered else self.color
        if self.disabled:
            color = Colors.PANEL
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, Colors.GRID, self.rect, width=2,
                         border_radius=8)

        font = self.font or Fonts.body
        text_color = Colors.TEXT_DIM if self.disabled else self.text_color
        text_surf = font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, event: pygame.event.Event) -> bool:
        if self.disabled:
            return False
        return (event.type == pygame.MOUSEBUTTONUP and event.button == 1
                and self.rect.collidepoint(event.pos))


# Text input widget
class TextInput:

    def __init__(self, x: int, y: int, w: int, h: int,
                 placeholder: str = "", max_length: int = 20,
                 initial: str = ""):
        self.rect = pygame.Rect(x, y, w, h)
        self.placeholder = placeholder
        self.max_length = max_length
        self.text = initial
        self._caret_timer = 0      # ms accumulator for blinking
        self._caret_visible = True

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            return True
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return False
        if event.key == pygame.K_SPACE:
            if len(self.text) < self.max_length:
                self.text += " "
            return False

        # Use event.unicode when available
        char = event.unicode
        if char and char.isprintable() and len(self.text) < self.max_length:
            self.text += char
            return False

        # Fallback: map key code to letter
        if pygame.K_a <= event.key <= pygame.K_z:
            letter = chr(ord('a') + (event.key - pygame.K_a))
            mods = getattr(event, "mod", 0) or pygame.key.get_mods()
            shift_held = bool(mods & (pygame.KMOD_SHIFT))
            caps_on    = bool(mods & (pygame.KMOD_CAPS))
            if shift_held ^ caps_on:  # XOR: one but not both
                letter = letter.upper()
            if len(self.text) < self.max_length:
                self.text += letter
            return False

        # Number keys
        if pygame.K_0 <= event.key <= pygame.K_9:
            digit = chr(ord('0') + (event.key - pygame.K_0))
            if len(self.text) < self.max_length:
                self.text += digit
            return False

        return False

    def update(self, dt_ms: int) -> None:
        self._caret_timer += dt_ms
        if self._caret_timer >= 500:
            self._caret_timer = 0
            self._caret_visible = not self._caret_visible

    def draw(self, surface: pygame.Surface) -> None:
        # Border + background
        pygame.draw.rect(surface, Colors.PANEL_LIGHT, self.rect,
                         border_radius=8)
        pygame.draw.rect(surface, Colors.ACCENT, self.rect, width=2,
                         border_radius=8)

        # Text or placeholder
        display = self.text if self.text else self.placeholder
        color = Colors.TEXT if self.text else Colors.TEXT_DIM
        font = Fonts.heading
        text_surf = font.render(display, True, color)
        text_rect = text_surf.get_rect(
            midleft=(self.rect.x + 14, self.rect.centery)
        )
        surface.blit(text_surf, text_rect)

        # Blinking caret
        if self._caret_visible:
            caret_x = text_rect.right + 2 if self.text else self.rect.x + 14
            caret_y_top = self.rect.y + 10
            caret_y_bot = self.rect.bottom - 10
            pygame.draw.line(surface, Colors.ACCENT,
                             (caret_x, caret_y_top),
                             (caret_x, caret_y_bot), 2)
