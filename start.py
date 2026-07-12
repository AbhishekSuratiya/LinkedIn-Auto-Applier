#!/usr/bin/env python3
"""
LinkedIn Auto Applier - Single Entry Point

Usage:
    python start.py

This script:
1. Loads configuration from config.json
2. Validates all required settings
3. Initializes the Tkinter overlay UI
4. Runs the browser + bot logic

Note: This all runs on a SINGLE thread deliberately. On macOS, Tkinter's
Aqua backend and Selenium's subprocess spawning (fork/exec of chromedriver
-> Chrome) both require the process's main thread; mixing them across
threads can hard-abort the process ("Tcl_WaitForEvent: Notifier not
initialized"). The UI is kept responsive via `SyncEventBus`, which pumps
Tk's event loop (`root.update()`) synchronously each time the bot emits an
event, instead of using a real `mainloop()` while the bot runs elsewhere.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_loader import load_config, validate_config
from ui import create_ui_window, keep_window_open_after_bot_finishes


def main():
    """Main entry point"""
    try:
        print("\n" + "="*70)
        print("   LinkedIn Auto Applier Bot")
        print("="*70 + "\n")

        # Step 1: Load configuration
        print("[1/4] Loading configuration...")
        config = load_config("config.json")
        validate_config(config)
        print("✓ Configuration loaded successfully\n")

        # Step 2: Initialize UI
        print("[2/4] Initializing UI...")
        overlay, event_bus, response_stub = create_ui_window(config)
        # Route safe_alert()/safe_confirm() (used throughout the bot for
        # pause/confirm prompts) through this overlay window instead of the
        # terminal, so the user never has to type answers into the shell.
        import modules.helpers as _helpers_module
        _helpers_module.set_active_overlay(overlay)
        print("✓ UI ready\n")

        # Step 3: Initialize browser (main thread - required on macOS)
        print("[3/4] Initializing browser...")
        from modules.open_chrome import initialize_driver
        driver, wait, actions = initialize_driver(config)
        print("✓ Browser initialized\n")

        # Step 4: Run the bot (main thread)
        print("[4/4] Starting bot...\n")
        from runAiBot import main as run_bot
        run_bot(config, driver, event_bus, response_stub, wait=wait, actions=actions)

        # Bot finished; keep the window open for review until user closes it.
        keep_window_open_after_bot_finishes(overlay)

    except KeyboardInterrupt:
        print("\n\n⚠ Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
