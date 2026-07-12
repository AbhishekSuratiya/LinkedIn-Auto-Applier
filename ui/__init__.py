"""
UI system for LinkedIn Auto Applier
Handles overlay window and event communication
"""

from ui.events import *
from ui.overlay import create_ui_window, keep_window_open_after_bot_finishes

__all__ = [
    "create_ui_window",
    "keep_window_open_after_bot_finishes",
    "JobStarted",
    "QuestionCollected",
    "PauseNeeded",
    "SubmissionReady",
    "UIResponse",
    "BotStatus",
]
