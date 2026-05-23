"""
data_manager.py — Persistent storage for high scores.

This module is imported by gui_game.py — do NOT run it directly.
Run `python main.py` instead.

Advanced topic demonstrated in this file:
    - File Input/Output (JSON read/write)
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


SCORES_FILE = os.path.join(os.path.dirname(__file__), "data", "scores.json")


def load_scores() -> List[Dict]:
    """Load the score history from disk; return [] if no file yet."""
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # File is corrupted or unreadable -- start fresh rather than crash
        return []


def save_score(player_name: str, score: int, total: int,
               ai_score: Optional[int] = None) -> None:
    """Append a new score record and persist it."""
    record = {
        "player": player_name,
        "score": score,
        "total": total,
        "accuracy": round(score / total, 3) if total else 0.0,
        "ai_score": ai_score,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    scores = load_scores()
    scores.append(record)

    # Make sure the data directory exists before writing
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)


def get_leaderboard(top_n: int = 5) -> List[Dict]:
    """Return the top-N records sorted by accuracy (descending)."""
    scores = load_scores()
    return sorted(scores, key=lambda r: r["accuracy"], reverse=True)[:top_n]
