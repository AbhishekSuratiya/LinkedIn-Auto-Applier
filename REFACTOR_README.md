# LinkedIn Auto Applier - Refactored Version

## What's New

This refactored version improves the user experience significantly:

### 🎯 Key Improvements

1. **Single Config File** - `config.json` replaces 6 scattered Python files
2. **Visual Overlay UI** - Always-visible Tkinter window showing real-time bot status
3. **Click-based Controls** - Pause/Resume/Discard buttons instead of terminal prompts
4. **Answer Editing** - Review and edit answers before submission
5. **Single Entry Point** - Run `python start.py` to start everything

---

## ✨ New Workflow

### Before (Old System)
```
Edit 6 config files → python runAiBot.py → Terminal popups block the bot
```

### After (New System)
```
Edit config.json → python start.py → Visual UI shows everything in real-time
```

---

## 🚀 Quick Start

### 1. First Run
```bash
python start.py
```

This will:
- Load `config.json`
- Show Tkinter overlay window
- Initialize browser
- Start applying to jobs

### 2. Edit Configuration
All settings are now in `config.json`. Open it and customize:
- `personal_info` - Your details (name, phone, address, etc.)
- `qa_answers` - Your canned answers (experience, salary, etc.)
- `search_preferences` - Job search filters
- `secrets` - LinkedIn credentials and AI API keys
- `behavior` - Bot behavior settings (pause_before_submit, run_in_background, etc.)
- `ui` - UI settings (allow_answer_editing, etc.)

Example:
```json
{
  "personal_info": {
    "first_name": "Your Name",
    "last_name": "Your Last Name",
    ...
  },
  "search_preferences": {
    "search_terms": ["React Developer", "Frontend Engineer"],
    ...
  }
}
```

### 3. Run the Bot
```bash
python start.py
```

A Tkinter window will appear showing:
- Current job (title, company, location)
- Recent 5 questions and answers
- Control buttons: Pause, Discard, Hide

---

## 📋 File Structure

### New Files
```
config.json                    # Main configuration file (user edits this)
config_loader.py              # Loads and validates config.json
start.py                       # Single entry point
ui/
  ├── __init__.py
  ├── events.py               # Event types for bot-UI communication
  ├── overlay.py              # Tkinter UI window
  └── constants.py            # (future) UI styling constants
test_config_load.py           # Quick test to verify config system
```

### Modified Files
```
runAiBot.py                    # Updated to use config dict and emit events
modules/open_chrome.py         # New initialize_driver(config) function
```

### Backward Compatible
The old Python config files still work if `config.json` is not present.

---

## 🔄 How the UI Works

### Overlay Window Features

**Status Header**
- Shows bot status: "● Searching", "● Job Found", "● Paused", etc.

**Current Job Section**
- Job ID, Title, Company, Location/WorkStyle

**Recent Questions Section**
- Last 5 questions with answers
- Scrollable for viewing history
- Current question highlighted with "→"

**Control Buttons**
- ⏸ **Pause/Resume** - Pause the bot, then click to resume
- ⛔ **Discard** - Skip current job (asks for confirmation)
- ⊟ **Hide** - Minimize window (bot keeps running)

**Dialogs**
- **Submission Confirmation** - Review all answers before submitting
- **Pause Dialog** - Shows reason for pause, click OK to resume
- **Window Close** - Choose to close UI (bot continues) or stop bot entirely

---

## ⚙️ Configuration Guide

### Personal Info
```json
"personal_info": {
  "first_name": "John",
  "middle_name": "",
  "last_name": "Doe",
  "phone_number": "1234567890",
  "current_city": "New York",
  "street": "123 Main St",
  "state": "NY",
  "zipcode": "10001",
  "country": "USA",
  "gender": "Male",
  "disability_status": "No",
  "veteran_status": "No"
}
```

### QA Answers
```json
"qa_answers": {
  "years_of_experience": "5",
  "desired_salary": 100000,
  "current_ctc": 80000,
  "linkedin_headline": "Software Engineer",
  "cover_letter": "I'm interested in this role because..."
}
```

### Search Preferences
```json
"search_preferences": {
  "search_terms": ["React Developer", "Frontend Engineer"],
  "experience_level": ["Mid-Senior level"],
  "job_type": ["Full-time"],
  "easy_apply_only": true
}
```

### Behavior Settings
```json
"behavior": {
  "pause_before_submit": true,      # Pause before submitting
  "run_in_background": false,       # Run in headless mode
  "stealth_mode": false,            # Avoid bot detection
  "keep_screen_awake": true         # Keep PC active
}
```

### UI Settings
```json
"ui": {
  "allow_answer_editing": true,     # Edit answers before submit
  "always_show_overlay": true,      # Keep window visible
  "show_recent_questions_count": 5  # Show last N questions
}
```

---

## 🔗 Event System (Advanced)

The bot communicates with the UI via events:

### Bot → UI Events
- `JobStarted` - New job found
- `QuestionCollected` - Question answered
- `BotStatus` - Status update (searching, paused, etc.)

### UI → Bot Events
- `UIResponse` - User clicked pause, discard, submit, etc.

Events are sent via `queue.Queue` for thread-safe communication.

---

## 🔄 Migration from Old System

### Option 1: Start Fresh with New Config
1. Delete old config files or keep them (they'll be ignored)
2. Edit `config.json` with your settings
3. Run `python start.py`

### Option 2: Auto-migrate (Future)
A migration script can convert old `.py` configs to `config.json` automatically.

---

## 🆘 Troubleshooting

### Config not loading
```bash
python test_config_load.py  # Test config system
```

### UI not appearing
- Tkinter may not be installed: `pip install tk`
- Try `config["ui"]["enable_tkinter_ui"] = false` to use terminal mode

### Bot not starting
- Check `config.json` syntax (use JSON validator)
- Verify all required fields are present
- Run with `python -u start.py` for unbuffered output

### Old config files
- Put them in a `config_backup/` folder if you want to keep them
- Or delete them (new system uses `config.json`)

---

## 📝 Notes

- **Backward Compatible**: Old way of running still works if no `config.json`
- **Terminal Fallback**: If Tkinter unavailable, uses terminal dialogs
- **Config Validation**: Invalid config.json won't run (clear error messages)
- **Event Logging**: UI events are logged for debugging

---

## 🎓 Understanding the New Architecture

### Flow Diagram
```
config.json
    ↓
start.py
    ├→ config_loader (validates)
    ├→ ui/overlay (creates Tkinter window)
    ├→ modules/open_chrome (initializes browser)
    └→ runAiBot.main() (starts bot)
        
runAiBot.main()
    ↓
apply_to_jobs() [emits JobStarted]
    ↓
answer_questions() [emits QuestionCollected]
    ↓
event_queue → UI updates display
    ↓
UI events ← response_queue
```

### Key Components

**config_loader.py**
- Loads JSON config
- Validates required fields
- Falls back to old `.py` config for compatibility

**ui/events.py**
- Defines all event types
- Used for bot ↔ UI communication

**ui/overlay.py**
- Tkinter window
- Listens to event_queue
- Sends responses via response_queue

**runAiBot.py** (modified)
- Emits events to UI
- Accepts config dict
- Passes queues to functions

---

## ✅ Checklist for First Run

- [ ] Edit `config.json` with your details
- [ ] Add your LinkedIn credentials to `secrets` section
- [ ] Verify `search_terms` list is not empty
- [ ] Run `python test_config_load.py` to verify setup
- [ ] Run `python start.py` to start bot
- [ ] Observe Tkinter window appearing
- [ ] Watch job being processed in real-time
- [ ] Test pause/resume with UI buttons

---

## 🚀 Next Steps / Known Issues

### Working
✅ Config consolidation (config.json)
✅ Config validation
✅ Tkinter UI with real-time updates
✅ Job and question display in UI
✅ Event emission system
✅ Single entry point (start.py)

### Needs Testing / Refinement
⚠️ Pause/Resume with UI buttons (queues implemented but not fully tested)
⚠️ Submission confirmation workflow
⚠️ Answer editing in UI
⚠️ Window close handling
⚠️ Full end-to-end run with actual LinkedIn

### Future Improvements
🔜 Answer editing form in UI
🔜 Submission summary dialog
🔜 Auto-migration script from old config
🔜 CSS styling for Tkinter window
🔜 Progress indicators (% complete)

---

## 💡 Tips

1. **Multiple runs**: UI shows history of recent questions
2. **Pause often**: Use pause button to review answers before submit
3. **Safe mode**: Set `safe_mode: true` if browser opening issues
4. **Logging**: Check `logs/log.txt` for detailed execution logs
5. **Dry run**: Test with `switch_number: 1` for first job only

---

## 📞 Support

- Check `logs/log.txt` for errors
- Run `test_config_load.py` to diagnose config issues
- Original README: [README.md](README.md)
- GitHub Issues: [LinkedIn-Auto-Applier](https://github.com/GodsScion/Auto_job_applier_linkedIn)

---

**Version**: 26.01.20 Refactored
**Updated**: 2026-07-11
