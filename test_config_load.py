#!/usr/bin/env python3
"""
Quick test to verify config loading and UI initialization
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing configuration system...\n")

# Test 1: Load config
print("[1/3] Testing config loader...")
try:
    from config_loader import load_config, validate_config
    config = load_config("config.json")
    validate_config(config)
    print("✓ Config loaded successfully")
    print(f"  - Search terms: {len(config['search_preferences']['search_terms'])} terms")
    print(f"  - Name: {config['personal_info']['first_name']} {config['personal_info']['last_name']}\n")
except Exception as e:
    print(f"✗ Config loading failed: {e}\n")
    sys.exit(1)

# Test 2: Import UI modules
print("[2/3] Testing UI modules...")
try:
    from ui import events, create_ui_window
    print("✓ UI modules imported successfully")
    print(f"  - Events available: JobStarted, QuestionCollected, PauseNeeded, etc.\n")
except Exception as e:
    print(f"✗ UI import failed: {e}\n")
    sys.exit(1)

# Test 3: Test event creation
print("[3/3] Testing event creation...")
try:
    job_event = events.JobStarted(
        job_id="123", title="Test", company="Google",
        work_location="NYC", work_style="Remote"
    )
    q_event = events.QuestionCollected(
        label="Experience", answer="5 years", question_type="text", prev_answer=None
    )
    print("✓ Events created successfully")
    print(f"  - JobStarted: {job_event.title} @ {job_event.company}")
    print(f"  - QuestionCollected: {q_event.label} → {q_event.answer}\n")
except Exception as e:
    print(f"✗ Event creation failed: {e}\n")
    sys.exit(1)

print("="*70)
print("All tests passed! ✓")
print("="*70)
print("\nYou can now run: python start.py")
