# Architecture: LinkedIn Auto Applier Refactor

## Overview

The refactored LinkedIn Auto Applier uses a modular architecture with:
- **Config System**: Single JSON configuration file
- **Event System**: Thread-safe bot ↔ UI communication
- **Tkinter UI**: Always-visible overlay window
- **Single Entry Point**: `start.py` orchestrates everything

---

## System Components

### 1. Config System

**Files**: `config.json`, `config_loader.py`

**Purpose**: Load and validate configuration from JSON

**Flow**:
```
config.json (user edits)
    ↓
config_loader.load_config()
    ↓
validate_config() (checks required fields)
    ↓
Returns: dict with all settings
```

**Key Functions**:
- `load_config(path)` - Load JSON config
- `validate_config(config)` - Validate structure
- Fallback to old Python configs if `.json` not found

**Data Structure**:
```python
config = {
    "personal_info": {...},
    "qa_answers": {...},
    "search_preferences": {...},
    "filtering": {...},
    "secrets": {...},
    "behavior": {...},
    "paths": {...},
    "performance": {...},
    "ui": {...}
}
```

---

### 2. Event System

**File**: `ui/events.py`

**Purpose**: Define all event types for bot ↔ UI communication

**Event Types**:

```python
# Bot → UI Events
@dataclass
class JobStarted:
    job_id: str
    title: str
    company: str
    work_location: str
    work_style: str

@dataclass
class QuestionCollected:
    label: str
    answer: Any
    question_type: str  # "select", "radio", "text", "textarea", "checkbox"
    prev_answer: Optional[Any]

@dataclass
class PauseNeeded:
    reason: str  # "submission_confirm", "stuck_question", etc.
    pause_type: str
    message: Optional[str]

@dataclass
class SubmissionReady:
    questions_list: List[tuple]
    job_title: str
    company: str
    job_id: str

@dataclass
class BotStatus:
    status: str  # "searching", "found_job", "answering", "paused", "submitting"
    current_job: Optional[dict]
    current_question: Optional[str]
    progress: Optional[str]
    message: Optional[str]

# UI → Bot Events
@dataclass
class UIResponse:
    action: str  # "resume", "discard", "submit", "edit", "logout"
    data: Optional[Any]
    edited_answers: Optional[dict]
```

**Communication Pattern**:
```
Bot Thread                          UI Thread
    │                                  │
    ├─ Create event                    │
    ├─ event_queue.put(event)         │
    │                    ─────────────→│
    │                                  ├─ Update display
    │                                  ├─ Wait for user action
    │                                  ├─ response_queue.put(response)
    │                    ←─────────────┤
    └─ response_queue.get()            │
       (blocks until response)         │
```

---

### 3. UI System (Tkinter)

**Files**: `ui/__init__.py`, `ui/overlay.py`, `ui/constants.py`

**Purpose**: Always-visible overlay showing bot status and controls

**Main Components**:

#### BotOverlay Class
- Tkinter window (stays on top)
- Sections:
  1. **Header**: Status indicator, title
  2. **Job Section**: Current job details
  3. **Questions Section**: Last 5 questions, scrollable
  4. **Controls**: Pause/Resume, Discard, Hide buttons
  5. **Dialogs**: Modal windows for confirmations

#### create_ui_window()
- Creates overlay in separate thread
- Returns `(event_queue, response_queue)` tuple
- Falls back gracefully if Tkinter unavailable

**Key Methods**:
```python
update_job(job: JobStarted)              # Update current job display
add_question(q: QuestionCollected)       # Add question to recent list
show_pause_dialog(pause: PauseNeeded)    # Show pause confirmation
show_submission_dialog(...)              # Show submission review
set_status(status: BotStatus)            # Update status indicator
reset_for_next_job()                     # Clear for next job
is_paused() → bool                       # Check pause state
should_discard() → bool                  # Check discard state
```

**Thread Safety**:
- Event loop runs in main UI thread
- Bot runs in main application thread
- Queue.Queue ensures thread-safe communication
- UI updates via `root.after()` to avoid GUI issues

---

### 4. Bot System

**File**: `runAiBot.py` (modified)

**Modified Functions**:

#### main(config, driver, event_queue, response_queue)
- Entry point
- Sets up config variables
- Stores global event queue references
- Calls run() to start job applying

#### apply_to_jobs(search_terms, event_queue, response_queue)
- Main loop over jobs
- Emits `JobStarted` for each job
- Calls `answer_questions()` with event_queue
- Handles job skipping/applying

#### answer_questions(..., event_queue)
- For each question (select, radio, text, etc.):
  - Answer the question
  - Emit `QuestionCollected` event
  - Continue to next question

#### run(total_runs, event_queue, response_queue)
- Orchestrates one cycle of job applications
- Calls `apply_to_jobs()`
- Handles multiple cycles if `run_non_stop`

**Backward Compatibility**:
- Global variables like `first_name`, `search_terms`, etc. still work
- Old config files still supported if config.json missing
- Can still be run directly without UI: `python runAiBot.py`

---

### 5. Browser Integration

**File**: `modules/open_chrome.py` (modified)

**New Function**:
```python
def initialize_driver(config: dict) -> WebDriver:
    """Initialize Selenium WebDriver with config dict"""
    # Extract settings from config
    # Create Chrome options
    # Initialize and return driver
```

**Backward Compatibility**:
- Old `createChromeSession()` still works
- Module-level driver initialization only if no `config.json`
- Both old and new flow supported

---

### 6. Entry Point

**File**: `start.py`

**Flow**:
```python
1. Load config from config.json
2. Validate config
3. Create UI (returns event/response queues)
4. Initialize browser driver
5. Call runAiBot.main(config, driver, event_queue, response_queue)
```

**Error Handling**:
- Clear error messages if config invalid
- Graceful fallback if Tkinter unavailable
- Help text for common issues

---

## Data Flow Diagram

```
start.py
  ├─→ config_loader.load_config("config.json")
  │     └─→ returns: config dict
  │
  ├─→ modules/open_chrome.initialize_driver(config)
  │     └─→ returns: WebDriver
  │
  ├─→ ui/overlay.create_ui_window(config)
  │     └─→ returns: (event_queue, response_queue)
  │     └─→ spawns: Tkinter window in thread
  │
  └─→ runAiBot.main(config, driver, event_queue, response_queue)
        │
        ├─→ _setup_config_vars(config)
        │     └─→ Extract config values to globals
        │
        ├─→ initialize AI client (if enabled)
        │
        └─→ run(total_runs, event_queue, response_queue)
              │
              └─→ apply_to_jobs(search_terms, event_queue, response_queue)
                    │
                    ├─→ For each job:
                    │   ├─→ JobStarted event → event_queue
                    │   │   (UI updates display)
                    │   │
                    │   └─→ answer_questions(..., event_queue)
                    │       ├─→ For each question:
                    │       │   └─→ QuestionCollected event → event_queue
                    │       │       (UI shows question)
                    │       │
                    │       └─→ Submission confirmation
                    │           (UI shows dialog, waits for response)
                    │
                    └─→ Log results to CSV
```

---

## Module Dependencies

```
start.py
  ├── config_loader.py
  ├── ui/
  │   ├── overlay.py
  │   ├── events.py
  │   └── __init__.py
  ├── modules/open_chrome.py
  │   └── modules/helpers.py
  └── runAiBot.py
      ├── config/ (old Python configs - for compatibility)
      ├── modules/clickers_and_finders.py
      ├── modules/helpers.py
      ├── modules/ai/
      └── modules/validator.py
```

---

## Configuration Precedence

1. **config.json** (new, preferred)
2. **Old Python config files** (fallback for compatibility)
3. **Hardcoded defaults** (if nothing else found)

```
if config.json exists:
    load from JSON
elif old config files exist:
    migrate from Python files
else:
    use hardcoded defaults
```

---

## Error Handling Strategy

### Config Loading
```python
try:
    config = load_config()
    validate_config(config)
except FileNotFoundError:
    print("❌ config.json not found")
except JSONDecodeError:
    print("❌ Invalid JSON in config.json")
except ValueError as e:
    print(f"❌ Missing required config field: {e}")
```

### UI Initialization
```python
try:
    event_queue, response_queue = create_ui_window(config)
except ImportError:
    print("⚠️ Tkinter not available, using terminal")
except Exception as e:
    print(f"⚠️ UI init failed, continuing without UI")
```

### Browser Initialization
```python
try:
    driver = initialize_driver(config)
except SessionNotCreatedException:
    print("❌ Chrome outdated, update browser")
except Exception:
    print("❌ Failed to initialize browser")
```

---

## Testing Strategy

**Unit Tests** (planned):
- `test_config_load.py` - Config loading
- Test config validation
- Test event creation
- Test event queue communication

**Integration Tests**:
- Full flow: config → UI → browser → job applying
- Pause/resume workflow
- Job skipping
- CSV logging

**Manual Tests**:
- Run with 1 job (`switch_number: 1`)
- Test pause button
- Test discard button
- Check CSV logs

---

## Performance Considerations

1. **Event Queue**: Lightweight, designed for 100+ events/run
2. **UI Updates**: Batched via `root.after()` to avoid blocking
3. **Thread Safety**: All queue operations are atomic
4. **Memory**: Config dict is small (~1KB), reusable across runs
5. **Startup**: Config loading is instant (~10ms)

---

## Future Enhancements

1. **Answer Editing**: Form in UI to edit answers before submit
2. **Progress Tracking**: Visual progress bar
3. **Multi-run Stats**: Dashboard showing runs, success rate
4. **Job Filtering**: UI controls to filter upcoming jobs
5. **Scheduled Runs**: Cron-like job scheduling
6. **Cloud Sync**: Backup config to cloud
7. **Web Dashboard**: Browser-based alternative to Tkinter

---

## Backward Compatibility

**Fully compatible** with old system:
- Old Python config files still work
- Can run `python runAiBot.py` directly (no start.py needed)
- Existing imports/globals unaffected
- CSV log format unchanged

**Migration Path**:
1. Keep old config files as backup
2. Create config.json from old settings
3. Run: `python start.py` (uses new system)
4. Or run: `python runAiBot.py` (uses old system)

---

## Security Notes

- **Credentials**: Stored in `secrets.config` section
  - Never commit `config.json` with real credentials
  - Add to `.gitignore`
- **API Keys**: Also in secrets section
  - Keep confidential
- **Browser**: Headless mode available
  - No credentials visible on screen

---

## Debugging

### Enable Verbose Logging
```python
# In start.py or runAiBot.py
print_lg("Debug message")  # Goes to logs/log.txt
```

### Event Queue Monitoring
```python
# Check what events are being sent
while True:
    try:
        event = event_queue.get_nowait()
        print(f"Event: {type(event).__name__}")
    except queue.Empty:
        break
```

### Config Inspection
```python
import json
with open("config.json") as f:
    config = json.load(f)
    print(json.dumps(config, indent=2))
```

---

## Summary

The refactored architecture provides:
- **Modularity**: Separate config, UI, events, bot logic
- **Flexibility**: Use UI or not, use old config or new
- **Maintainability**: Clear event contracts, type hints
- **Extensibility**: Easy to add new events, UI features, etc.
- **Reliability**: Error handling, graceful fallbacks, validation
- **Performance**: Minimal overhead, async-ready

All while maintaining 100% backward compatibility with the original system.
