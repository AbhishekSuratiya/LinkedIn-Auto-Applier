"""
Tkinter overlay UI for LinkedIn Auto Applier
Always-visible window showing bot status and real-time updates
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import queue
import threading
from typing import Tuple, Optional
from collections import deque
from ui.events import *


class BotOverlay:
    """Main overlay window for bot status and controls"""

    def __init__(self, config: dict):
        self.config = config
        self.root = tk.Tk()
        self.root.title("LinkedIn Auto Applier — Starting...")
        self.root.geometry("580x760")
        self.root.resizable(True, True)

        # Make window stay on top
        self.root.attributes('-topmost', True)

        # Colors
        self.bg_color = "#f0f0f0"
        self.header_color = "#2c3e50"
        self.accent_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#e74c3c"

        self.root.configure(bg=self.bg_color)

        # macOS's native ("aqua") ttk/tk button rendering ignores custom
        # background colors and can end up drawing white text on a white
        # native button face (invisible). The "clam" theme is a
        # non-native, fully custom-drawn theme that actually respects
        # background/foreground colors cross-platform.
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass  # theme unavailable; fall back to whatever's default

        self.neutral_color = "#95a5a6"
        for name, color in (
            ("Accent", self.accent_color),
            ("Warning", self.warning_color),
            ("Success", self.success_color),
            ("Neutral", self.neutral_color),
        ):
            self.style.configure(
                f"{name}.TButton",
                background=color, foreground="white",
                font=("Arial", 12, "bold"), padding=8, borderwidth=0,
            )
            self.style.map(
                f"{name}.TButton",
                background=[("active", color), ("pressed", color)],
                foreground=[("active", "white"), ("pressed", "white")],
            )

        # Recent questions tracking
        self.recent_questions = deque(maxlen=config["ui"]["show_recent_questions_count"])
        self.all_questions = []
        self.submitted = False
        self.paused = False
        self.pause_reason = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup all UI elements"""
        # Header
        self._setup_header()

        # Status frame
        self._setup_status_frame()

        # Questions frame
        self._setup_questions_frame()

        # Controls frame
        self._setup_controls_frame()

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _setup_header(self):
        """Header with title and status indicator"""
        header = tk.Frame(self.root, bg=self.header_color, height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        title = tk.Label(
            header, text="LinkedIn Auto Applier",
            font=("Arial", 18, "bold"), fg="white", bg=self.header_color
        )
        title.pack(side=tk.LEFT, padx=10, pady=5)

        self.status_label = tk.Label(
            header, text="● Initializing",
            font=("Arial", 13), fg=self.accent_color, bg=self.header_color
        )
        self.status_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def _setup_status_frame(self):
        """Current job and progress info"""
        frame = tk.LabelFrame(
            self.root, text="Current Job", font=("Arial", 13, "bold"),
            bg=self.bg_color, fg=self.header_color, padx=10, pady=10
        )
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Job ID
        tk.Label(frame, text="Job ID:", font=("Arial", 13, "bold"), bg=self.bg_color, fg="#222").pack(anchor=tk.W)
        self.job_id_label = tk.Label(frame, text="—", font=("Arial", 13), bg=self.bg_color, fg="#555")
        self.job_id_label.pack(anchor=tk.W, padx=(20, 0), pady=(0, 5))

        # Title
        tk.Label(frame, text="Title:", font=("Arial", 13, "bold"), bg=self.bg_color, fg="#222").pack(anchor=tk.W)
        self.job_title_label = tk.Label(frame, text="—", font=("Arial", 13), bg=self.bg_color, fg="#555", wraplength=440, justify=tk.LEFT)
        self.job_title_label.pack(anchor=tk.W, padx=(20, 0), pady=(0, 5))

        # Company
        tk.Label(frame, text="Company:", font=("Arial", 13, "bold"), bg=self.bg_color, fg="#222").pack(anchor=tk.W)
        self.job_company_label = tk.Label(frame, text="—", font=("Arial", 13), bg=self.bg_color, fg="#555")
        self.job_company_label.pack(anchor=tk.W, padx=(20, 0), pady=(0, 5))

        # Location
        tk.Label(frame, text="Location:", font=("Arial", 13, "bold"), bg=self.bg_color, fg="#222").pack(anchor=tk.W)
        self.job_location_label = tk.Label(frame, text="—", font=("Arial", 13), bg=self.bg_color, fg="#555")
        self.job_location_label.pack(anchor=tk.W, padx=(20, 0), pady=(0, 0))

    def _setup_questions_frame(self):
        """Recent questions display"""
        frame = tk.LabelFrame(
            self.root, text="Recent Questions (Last 5)", font=("Arial", 13, "bold"),
            bg=self.bg_color, fg=self.header_color, padx=10, pady=10
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollable text area
        self.questions_text = scrolledtext.ScrolledText(
            frame, height=10, font=("Courier", 11),
            bg="white", fg="#333", wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.questions_text.pack(fill=tk.BOTH, expand=True)

    def _setup_controls_frame(self):
        """Control buttons"""
        frame = tk.Frame(self.root, bg=self.bg_color)
        frame.pack(fill=tk.X, padx=10, pady=10)

        self.pause_resume_btn = ttk.Button(
            frame, text="Pause", style="Warning.TButton", width=12,
            command=self._on_pause_resume
        )
        self.pause_resume_btn.pack(side=tk.LEFT, padx=5)

        self.discard_btn = ttk.Button(
            frame, text="Discard", style="Warning.TButton", width=12,
            command=self._on_discard
        )
        self.discard_btn.pack(side=tk.LEFT, padx=5)

        self.hide_btn = ttk.Button(
            frame, text="Hide", style="Neutral.TButton", width=12,
            command=self._on_hide
        )
        self.hide_btn.pack(side=tk.LEFT, padx=5)

    def _on_pause_resume(self):
        """Pause/Resume button click"""
        self.paused = not self.paused
        if self.paused:
            self.pause_resume_btn.config(text="Resume", style="Success.TButton")
        else:
            self.pause_resume_btn.config(text="Pause", style="Warning.TButton")

    def _on_discard(self):
        """Discard current job"""
        if messagebox.askyesno("Confirm", "Discard current application?"):
            self.discard_btn.config(state=tk.DISABLED)

    def _on_hide(self):
        """Minimize window"""
        self.root.withdraw()

    def _on_window_close(self):
        """Handle window close"""
        response = messagebox.askyesnocancel(
            "Close Window",
            "Close UI window?\n\nYes: Close UI, bot continues\nNo: Stop bot\nCancel: Keep UI open"
        )
        if response is True:
            # Close UI only
            self.root.withdraw()
        elif response is False:
            # Stop bot
            self.root.quit()

    def update_job(self, job: JobStarted):
        """Update job display"""
        self.job_id_label.config(text=job.job_id)
        self.job_title_label.config(text=job.title)
        self.job_company_label.config(text=job.company)
        self.job_location_label.config(text=f"{job.work_location} ({job.work_style})")
        self.status_label.config(text="● Job Found", fg=self.accent_color)

    def add_question(self, question: QuestionCollected):
        """Add question to recent questions list"""
        q_text = f"{question.label}: {question.answer} [{question.question_type}]"
        self.recent_questions.append(q_text)
        self.all_questions.append({
            "label": question.label,
            "answer": question.answer,
            "type": question.question_type,
            "prev_answer": question.prev_answer
        })
        self._update_questions_display()

    def _update_questions_display(self):
        """Refresh questions display"""
        self.questions_text.config(state=tk.NORMAL)
        self.questions_text.delete("1.0", tk.END)

        for i, q in enumerate(self.recent_questions, 1):
            is_last = i == len(self.recent_questions)
            prefix = "→ " if is_last else "  "
            self.questions_text.insert(tk.END, f"{prefix}{q}\n")

        self.questions_text.config(state=tk.DISABLED)
        self.questions_text.see(tk.END)

    def alert(self, text: str, title: str = "Alert", button: str = "Okay") -> str:
        """
        Generic single-button alert dialog, shown as a child window of the
        overlay (same Tk root/thread — no separate ad-hoc Tk instance, no
        terminal input()). Blocks until the user dismisses it.
        """
        return self.confirm(text, title, [button])

    def confirm(self, text: str, title: str = "Confirm", buttons: list[str] = None) -> str:
        """
        Generic multi-button confirmation dialog with arbitrary button
        labels (mirrors modules.helpers.safe_confirm's contract). Shown as a
        modal child window of the overlay. Blocks until a button is clicked
        or the dialog is closed (closing counts as clicking the last button,
        matching the "Cancel"-like semantics most callers expect).

        Returns the text of the button clicked.
        """
        if buttons is None:
            buttons = ["OK", "Cancel"]

        result = {"choice": buttons[-1]}

        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.configure(bg=self.bg_color)
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        msg_label = tk.Label(
            dialog, text=text, font=("Arial", 13), bg=self.bg_color, fg="#222",
            wraplength=420, justify=tk.LEFT, padx=20, pady=15
        )
        msg_label.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        def on_choice(choice):
            result["choice"] = choice
            dialog.destroy()

        for b in buttons:
            ttk.Button(
                btn_frame, text=b, style="Accent.TButton",
                command=lambda b=b: on_choice(b)
            ).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        dialog.protocol("WM_DELETE_WINDOW", lambda: on_choice(buttons[-1]))

        # Center over the main window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")

        self.root.wait_window(dialog)
        return result["choice"]

    def show_pause_dialog(self, pause: PauseNeeded):
        """Show pause confirmation dialog"""
        self.status_label.config(text="● Paused", fg=self.warning_color)
        self.pause_reason = pause.reason

        result = messagebox.showinfo(
            "Paused",
            f"{pause.message or pause.reason}\n\nClick OK to resume."
        )
        return result

    def show_submission_dialog(self, submission: SubmissionReady):
        """Show submission confirmation"""
        # Format all questions
        q_text = f"Job: {submission.job_title}\nCompany: {submission.company}\n\nQuestions:\n"
        for label, answer, q_type, _ in submission.questions_list:
            q_text += f"\n• {label}: {answer}"

        result = messagebox.askyesno(
            "Confirm Submission",
            q_text + "\n\nSubmit application?"
        )
        return result

    def set_status(self, status: BotStatus):
        """Update bot status"""
        status_map = {
            "searching": ("● Searching", self.accent_color),
            "found_job": ("● Job Found", self.success_color),
            "answering": ("● Answering", self.accent_color),
            "paused": ("● Paused", self.warning_color),
            "submitting": ("● Submitting", self.accent_color),
        }

        text, color = status_map.get(status.status, ("● Running", self.accent_color))
        if status.message:
            text += f" ({status.message})"

        self.status_label.config(text=text, fg=color)
        self.root.update()

    def run(self):
        """Run the UI event loop"""
        self.root.mainloop()

    def is_paused(self) -> bool:
        """Check if bot is paused"""
        return self.paused

    def should_discard(self) -> bool:
        """Check if user clicked discard"""
        return self.discard_btn.cget("state") == tk.DISABLED

    def reset_for_next_job(self):
        """Reset UI for next job"""
        self.recent_questions.clear()
        self.all_questions.clear()
        self.pause_resume_btn.config(state=tk.NORMAL, text="⏸ Pause", bg=self.warning_color)
        self.discard_btn.config(state=tk.NORMAL)
        self._update_questions_display()


class SyncEventBus:
    """
    Drop-in replacement for `queue.Queue` used by the bot to emit UI events.

    IMPORTANT (macOS): Tkinter's Aqua backend and Selenium's subprocess
    spawning (fork/exec of chromedriver -> Chrome) both need to happen on
    the process's main thread — macOS Cocoa/CoreFoundation forbids forking
    from a background thread once frameworks like Tk are loaded, and doing
    so can corrupt Tcl's own event notifier, hard-aborting the process with
    "Tcl_WaitForEvent: Notifier not initialized". So instead of running the
    bot on a background thread and the UI mainloop on the main thread (the
    "obvious" design), everything here runs on a single thread: `.put()`
    applies the event to the overlay immediately and pumps Tk's event loop
    via `root.update()` — no `mainloop()`, no threads, no cross-thread Tk
    calls, ever.
    """

    def __init__(self, overlay: Optional["BotOverlay"]):
        self.overlay = overlay

    def put(self, event) -> None:
        overlay = self.overlay
        if overlay is None:
            return
        try:
            if isinstance(event, JobStarted):
                overlay.update_job(event)
            elif isinstance(event, QuestionCollected):
                overlay.add_question(event)
            elif isinstance(event, PauseNeeded):
                overlay.show_pause_dialog(event)
            elif isinstance(event, SubmissionReady):
                overlay.show_submission_dialog(event)
            elif isinstance(event, BotStatus):
                overlay.set_status(event)

            if overlay.is_paused():
                overlay.status_label.config(text="● Paused", fg=overlay.warning_color)

            # Pump pending Tk events/redraws without entering a blocking mainloop.
            overlay.root.update_idletasks()
            overlay.root.update()
        except tk.TclError:
            # Window was closed by the user; keep the bot running headless.
            self.overlay = None


class NullResponseQueue:
    """Stub with a `.get()` that always returns None; nothing consumes real
    responses today (pause/submit confirmation is handled synchronously via
    dialogs inside SyncEventBus.put), but functions accept it for API
    compatibility."""

    def get(self, *args, **kwargs):
        return None

    def put(self, *args, **kwargs) -> None:
        pass


def create_ui_window(config: dict) -> Tuple[Optional[BotOverlay], SyncEventBus, NullResponseQueue]:
    """
    Create the overlay UI window. Everything (UI + bot) is expected to run
    on this same (main) thread afterward — see `SyncEventBus` for why.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (overlay_or_None, event_bus, response_stub)
    """
    if not config.get("ui", {}).get("enable_tkinter_ui", True):
        return None, SyncEventBus(None), NullResponseQueue()

    try:
        overlay = BotOverlay(config)
        print("✓ Tkinter UI initialized")
        return overlay, SyncEventBus(overlay), NullResponseQueue()
    except Exception as e:
        print(f"⚠ Failed to initialize Tkinter UI: {e}")
        print("✓ Falling back to terminal dialogs")
        return None, SyncEventBus(None), NullResponseQueue()


def keep_window_open_after_bot_finishes(overlay: Optional[BotOverlay]) -> None:
    """
    Call once the bot has finished running (main thread, no more Selenium
    subprocess spawning to worry about). Enters a real `mainloop()` so the
    window stays interactive for the user to review, until they close it.
    """
    if overlay is None:
        return
    try:
        overlay.status_label.config(text="● Finished", fg=overlay.success_color)
        overlay.root.mainloop()
    except tk.TclError:
        pass
