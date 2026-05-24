
import numpy as np
import pygame
from typing import Optional

from ui import Colors, Fonts
from eeg_generator import BRAIN_STATES


def draw_waveform_panel(surface: pygame.Surface, rect: pygame.Rect,
                        signal: np.ndarray, duration: float,
                        scroll_offset: int = 0,
                        window_samples: Optional[int] = None,
                        animated: bool = False) -> None:
    # Background panel
    pygame.draw.rect(surface, Colors.PANEL, rect, border_radius=6)

    # Title
    title_str = "Live EEG" if animated else "Time Domain"
    title = Fonts.heading.render(title_str, True, Colors.TEXT)
    surface.blit(title, (rect.x + 10, rect.y + 5))

    # "REC" indicator while animated (clinical look)
    if animated:
        rec_x = rect.x + 130
        rec_y = rect.y + 16
        pygame.draw.circle(surface, Colors.ERROR, (rec_x, rec_y), 6)
        rec_lbl = Fonts.small.render("LIVE", True, Colors.ERROR)
        surface.blit(rec_lbl, (rec_x + 12, rec_y - 8))

    # Compute plotting area (leave room for title)
    plot_x = rect.x + 10
    plot_y = rect.y + 35
    plot_w = rect.w - 20
    plot_h = rect.h - 45

    n_channels, n_samples = signal.shape
    channel_h = plot_h / n_channels

    if window_samples is None:
        window_samples = n_samples
    window_samples = min(window_samples, n_samples)

    # Horizontal grid lines + channel labels
    for ch in range(n_channels):
        baseline_y = plot_y + channel_h * (ch + 0.5)
        pygame.draw.line(surface, Colors.GRID,
                         (plot_x, int(baseline_y)),
                         (plot_x + plot_w, int(baseline_y)), 1)
        lbl = Fonts.small.render(f"Ch{ch + 1}", True, Colors.TEXT_DIM)
        surface.blit(lbl, (plot_x + 2, int(baseline_y) - 16))

    # Time axis label
    t_label = Fonts.small.render(f"{duration:.1f}s window",
                                 True, Colors.TEXT_DIM)
    surface.blit(t_label, (plot_x + plot_w - 90, plot_y + plot_h + 2))

    # Build the visible window via numpy roll, so scrolling wraps cleanly
    # without ever showing an empty edge.
    visible = np.roll(signal, -scroll_offset, axis=1)[:, :window_samples]

    # Normalize amplitude per channel so each fits its lane
    for ch in range(n_channels):
        ch_signal = visible[ch]
        max_abs = float(np.max(np.abs(ch_signal))) or 1.0
        scale = (channel_h * 0.4) / max_abs

        baseline_y = plot_y + channel_h * (ch + 0.5)
        color = Colors.CHANNELS[ch % len(Colors.CHANNELS)]

        # Downsample so we don't draw more points than we have pixels
        step = max(1, window_samples // plot_w)
        points = []
        for i in range(0, window_samples, step):
            x = plot_x + (i / window_samples) * plot_w
            y = baseline_y - ch_signal[i] * scale
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(surface, color, False, points, 1)

    # Sweeping cursor on the right edge during animation
    if animated:
        cursor_x = plot_x + plot_w - 1
        pygame.draw.line(surface, Colors.ACCENT,
                         (cursor_x, plot_y),
                         (cursor_x, plot_y + plot_h), 2)


def draw_spectrum_panel(surface: pygame.Surface, rect: pygame.Rect,
                        freqs: np.ndarray, power: np.ndarray,
                        max_freq: float = 50.0,
                        reveal_state: Optional[str] = None) -> None:
    pygame.draw.rect(surface, Colors.PANEL, rect, border_radius=6)

    title = Fonts.heading.render("Power Spectrum", True, Colors.TEXT)
    surface.blit(title, (rect.x + 10, rect.y + 5))

    plot_x = rect.x + 40
    plot_y = rect.y + 35
    plot_w = rect.w - 50
    plot_h = rect.h - 60

    # Trim to the visible frequency range
    mask = freqs <= max_freq
    f = freqs[mask]
    p = power[mask]

    # Log-scale conversion (avoid log(0))
    log_p = np.log10(p + 1e-6)
    log_min = float(log_p.min())
    log_max = float(log_p.max())
    log_range = max(log_max - log_min, 1e-6)

    # Shade the brain state's band if revealed
    if reveal_state and reveal_state in BRAIN_STATES:
        low, high = BRAIN_STATES[reveal_state]["band"]
        x_low  = plot_x + (low  / max_freq) * plot_w
        x_high = plot_x + (high / max_freq) * plot_w
        band_color = Colors.STATES.get(reveal_state, Colors.ACCENT)
        # Translucent shade via a separate surface
        shade = pygame.Surface((int(x_high - x_low), plot_h), pygame.SRCALPHA)
        shade.fill((*band_color, 60))
        surface.blit(shade, (int(x_low), plot_y))

    # Frequency grid lines every 10 Hz
    for hz in range(0, int(max_freq) + 1, 10):
        x = plot_x + (hz / max_freq) * plot_w
        pygame.draw.line(surface, Colors.GRID,
                         (int(x), plot_y),
                         (int(x), plot_y + plot_h), 1)
        lbl = Fonts.small.render(f"{hz}", True, Colors.TEXT_DIM)
        surface.blit(lbl, (int(x) - 6, plot_y + plot_h + 2))

    # Axis labels
    hz_lbl = Fonts.small.render("Hz", True, Colors.TEXT_DIM)
    surface.blit(hz_lbl, (plot_x + plot_w + 5, plot_y + plot_h - 6))

    # Plot spectrum as a filled area
    points = [(plot_x, plot_y + plot_h)]
    for i, freq in enumerate(f):
        x = plot_x + (freq / max_freq) * plot_w
        y_norm = (log_p[i] - log_min) / log_range
        y = plot_y + plot_h - y_norm * plot_h
        points.append((x, y))
    points.append((plot_x + plot_w, plot_y + plot_h))

    if len(points) >= 3:
        pygame.draw.polygon(surface, Colors.PANEL_LIGHT, points)
        # Outline on top
        pygame.draw.lines(surface, Colors.ACCENT, False, points[1:-1], 2)
