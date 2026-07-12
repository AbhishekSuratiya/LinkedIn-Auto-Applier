"""
Event types for bot-UI communication
"""

from dataclasses import dataclass
from typing import Any, Optional, List


@dataclass
class JobStarted:
    """Emitted when bot starts processing a job"""
    job_id: str
    title: str
    company: str
    work_location: str
    work_style: str


@dataclass
class QuestionCollected:
    """Emitted when a question is answered"""
    label: str
    answer: Any
    question_type: str  # "select", "radio", "text", "textarea", "checkbox"
    prev_answer: Optional[Any]


@dataclass
class PauseNeeded:
    """Emitted when bot needs user confirmation"""
    reason: str  # "submission_confirm", "stuck_question", "filters_review", "manual_login"
    pause_type: str  # "dialog", "modal"
    message: Optional[str] = None


@dataclass
class SubmissionReady:
    """Emitted before final submission"""
    questions_list: List[tuple]
    job_title: str
    company: str
    job_id: str


@dataclass
class UIResponse:
    """Response from UI back to bot"""
    action: str  # "resume", "discard", "submit", "edit", "logout"
    data: Optional[Any] = None
    edited_answers: Optional[dict] = None


@dataclass
class BotStatus:
    """Real-time bot status update"""
    status: str  # "searching", "found_job", "answering", "paused", "submitting"
    current_job: Optional[dict] = None
    current_question: Optional[str] = None
    progress: Optional[str] = None  # "Job 1/30", etc.
    message: Optional[str] = None
