"""
Config loader for LinkedIn Auto Applier
Loads and validates configuration from config.json
"""

import json
import os
from typing import Dict, Any

CONFIG_FILE = "config.json"
CONFIG_BACKUP = "config/personals.py"


def load_config(config_path: str = CONFIG_FILE) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    If config.json doesn't exist, falls back to old config files.

    Args:
        config_path: Path to config.json

    Returns:
        Dictionary containing all configuration
    """
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✓ Loaded config from {config_path}")
            return config
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing {config_path}: {e}")
            raise
        except Exception as e:
            print(f"✗ Error loading {config_path}: {e}")
            raise
    else:
        print(f"⚠ {config_path} not found. Attempting to load from legacy config files...")
        return load_legacy_config()


def load_legacy_config() -> Dict[str, Any]:
    """
    Fallback: Load configuration from old Python config files.
    This maintains backward compatibility.
    """
    try:
        # Import old config modules
        from config.personals import (
            first_name, middle_name, last_name, phone_number, current_city,
            street, state, zipcode, country, ethnicity, gender, disability_status, veteran_status
        )
        from config.questions import (
            default_resume_path, years_of_experience, require_visa, website, linkedIn,
            us_citizenship, desired_salary, current_ctc, notice_period, linkedin_headline,
            linkedin_summary, cover_letter, user_information_all, recent_employer, confidence_level,
            pause_before_submit, pause_at_failed_question, overwrite_previous_answers
        )
        from config.search import (
            search_terms, search_location, switch_number, randomize_search_order,
            sort_by, date_posted, salary, easy_apply_only, experience_level, job_type,
            on_site, companies, location, industry, job_function, job_titles, benefits,
            commitments, under_10_applicants, in_your_network, fair_chance_employer,
            pause_after_filters, about_company_bad_words, about_company_good_words,
            bad_words, security_clearance, did_masters, current_experience
        )
        from config.secrets import (
            username, password, use_AI, ai_provider, llm_model, llm_api_url, llm_api_key, stream_output
        )
        from config.settings import (
            close_tabs, follow_companies, run_non_stop, alternate_sortby, cycle_date_posted,
            stop_date_cycle_at_24hr, generated_resume_path, file_name, failed_file_name,
            logs_folder_path, click_gap, run_in_background, disable_extensions, safe_mode,
            smooth_scroll, keep_screen_awake, stealth_mode, showAiErrorAlerts, use_terminal_for_dialogs
        )

        # Reconstruct config dict
        config = {
            "personal_info": {
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "current_city": current_city,
                "street": street,
                "state": state,
                "zipcode": zipcode,
                "country": country,
                "ethnicity": ethnicity,
                "gender": gender,
                "disability_status": disability_status,
                "veteran_status": veteran_status,
            },
            "qa_answers": {
                "default_resume_path": default_resume_path,
                "years_of_experience": years_of_experience,
                "require_visa": require_visa,
                "website": website,
                "linkedIn": linkedIn,
                "us_citizenship": us_citizenship,
                "desired_salary": desired_salary,
                "current_ctc": current_ctc,
                "notice_period": notice_period,
                "linkedin_headline": linkedin_headline,
                "linkedin_summary": linkedin_summary,
                "cover_letter": cover_letter,
                "user_information_all": user_information_all,
                "recent_employer": recent_employer,
                "confidence_level": confidence_level,
            },
            "search_preferences": {
                "search_terms": search_terms,
                "search_location": search_location,
                "switch_number": switch_number,
                "randomize_search_order": randomize_search_order,
                "sort_by": sort_by,
                "date_posted": date_posted,
                "salary": salary,
                "easy_apply_only": easy_apply_only,
                "experience_level": experience_level,
                "job_type": job_type,
                "on_site": on_site,
                "companies": companies,
                "location": location,
                "industry": industry,
                "job_function": job_function,
                "job_titles": job_titles,
                "benefits": benefits,
                "commitments": commitments,
                "under_10_applicants": under_10_applicants,
                "in_your_network": in_your_network,
                "fair_chance_employer": fair_chance_employer,
                "pause_after_filters": pause_after_filters,
            },
            "filtering": {
                "about_company_bad_words": about_company_bad_words,
                "about_company_good_words": about_company_good_words,
                "bad_words": bad_words,
                "security_clearance": security_clearance,
                "did_masters": did_masters,
                "current_experience": current_experience,
            },
            "secrets": {
                "linkedin_username": username,
                "linkedin_password": password,
                "use_AI": use_AI,
                "ai_provider": ai_provider,
                "llm_model": llm_model,
                "llm_api_url": llm_api_url,
                "llm_api_key": llm_api_key,
                "stream_output": stream_output,
            },
            "behavior": {
                "pause_before_submit": pause_before_submit,
                "pause_at_failed_question": pause_at_failed_question,
                "overwrite_previous_answers": overwrite_previous_answers,
                "close_tabs": close_tabs,
                "follow_companies": follow_companies,
                "run_non_stop": run_non_stop,
                "alternate_sortby": alternate_sortby,
                "cycle_date_posted": cycle_date_posted,
                "stop_date_cycle_at_24hr": stop_date_cycle_at_24hr,
                "run_in_background": run_in_background,
                "disable_extensions": disable_extensions,
                "safe_mode": safe_mode,
                "smooth_scroll": smooth_scroll,
                "keep_screen_awake": keep_screen_awake,
                "stealth_mode": stealth_mode,
                "showAiErrorAlerts": showAiErrorAlerts,
                "use_terminal_for_dialogs": use_terminal_for_dialogs,
            },
            "paths": {
                "file_name": file_name,
                "failed_file_name": failed_file_name,
                "logs_folder_path": logs_folder_path,
                "generated_resume_path": generated_resume_path,
            },
            "performance": {
                "click_gap": click_gap,
            },
            "ui": {
                "allow_answer_editing": True,
                "always_show_overlay": True,
                "show_recent_questions_count": 5,
                "enable_tkinter_ui": True,
            }
        }

        print("✓ Loaded config from legacy Python config files")
        return config

    except ImportError as e:
        print(f"✗ Could not load legacy config: {e}")
        print(f"✓ Please create config.json or ensure config/ files exist")
        raise


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate that required config fields are present.

    Args:
        config: Configuration dictionary

    Raises:
        ValueError: If required fields are missing
    """
    required_sections = [
        "personal_info", "qa_answers", "search_preferences",
        "secrets", "behavior", "paths", "ui"
    ]

    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")

    # Validate personal_info
    personal_required = ["first_name", "last_name", "phone_number"]
    for field in personal_required:
        if field not in config["personal_info"]:
            raise ValueError(f"Missing required personal_info field: {field}")

    # Validate search_preferences
    if "search_terms" not in config["search_preferences"]:
        raise ValueError("Missing required search_preferences.search_terms")

    if not isinstance(config["search_preferences"]["search_terms"], list):
        raise ValueError("search_terms must be a list")

    if len(config["search_preferences"]["search_terms"]) == 0:
        raise ValueError("search_terms cannot be empty")

    print("✓ Config validation passed")
