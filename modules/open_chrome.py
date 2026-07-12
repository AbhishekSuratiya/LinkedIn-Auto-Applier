'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''

from modules.helpers import get_default_temp_profile, make_directories

# Try to import old config for backward compatibility
try:
    from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
    from config.questions import default_resume_path
    _has_old_config = True
except ImportError:
    _has_old_config = False
    run_in_background = False
    stealth_mode = False
    disable_extensions = False
    safe_mode = True
    file_name = "all excels/all_applied_applications_history.csv"
    failed_file_name = "all excels/all_failed_applications_history.csv"
    logs_folder_path = "logs/"
    generated_resume_path = "all resumes/"
    default_resume_path = "all resumes/default/resume.pdf"

if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg, get_chrome_major_version, safe_alert
from selenium.common.exceptions import SessionNotCreatedException

def initialize_driver(config: dict = None, isRetry: bool = False):
    """
    Initialize Selenium WebDriver with config

    Args:
        config: Configuration dictionary
        isRetry: Whether this is a retry with guest profile

    Returns:
        Tuple of (driver, wait, actions)
    """
    if config is None:
        # Fallback to old config
        _options, _driver, _actions, _wait = createChromeSession(isRetry)
        return _driver, _wait, _actions
    else:
        # Use config dict
        behavior = config.get("behavior", {})
        paths = config.get("paths", {})
        qa = config.get("qa_answers", {})

        cfg_run_in_background = behavior.get("run_in_background", False)
        cfg_stealth_mode = behavior.get("stealth_mode", False)
        cfg_disable_extensions = behavior.get("disable_extensions", False)
        cfg_safe_mode = behavior.get("safe_mode", True)
        cfg_file_name = paths.get("file_name", "all excels/all_applied_applications_history.csv")
        cfg_failed_file_name = paths.get("failed_file_name", "all excels/all_failed_applications_history.csv")
        cfg_logs_folder_path = paths.get("logs_folder_path", "logs/")
        cfg_generated_resume_path = paths.get("generated_resume_path", "all resumes/")
        cfg_default_resume_path = qa.get("default_resume_path", "all resumes/default/resume.pdf")

        _options, _driver, _actions, _wait = _createChromeSession(
            isRetry, cfg_run_in_background, cfg_stealth_mode, cfg_disable_extensions,
            cfg_safe_mode, cfg_file_name, cfg_failed_file_name, cfg_logs_folder_path,
            cfg_generated_resume_path, cfg_default_resume_path
        )
        return _driver, _wait, _actions


def createChromeSession(isRetry: bool = False):
    """Backward compatible wrapper"""
    return _createChromeSession(
        isRetry, run_in_background, stealth_mode, disable_extensions,
        safe_mode, file_name, failed_file_name, logs_folder_path,
        generated_resume_path, default_resume_path
    )


def _createChromeSession(
    isRetry: bool = False,
    run_in_background: bool = False,
    stealth_mode: bool = False,
    disable_extensions: bool = False,
    safe_mode: bool = True,
    file_name: str = "",
    failed_file_name: str = "",
    logs_folder_path: str = "",
    generated_resume_path: str = "",
    default_resume_path: str = ""
):
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if stealth_mode else Options()
    if run_in_background:   options.add_argument("--headless")
    if disable_extensions:  options.add_argument("--disable-extensions")

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
    profile_dir = find_default_profile_directory()
    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved in the browser!")
    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")
    if stealth_mode:
        # try: 
        #     driver = uc.Chrome(driver_executable_path="C:\\Program Files\\Google\\Chrome\\chromedriver-win64\\chromedriver.exe", options=options)
        # except (FileNotFoundError, PermissionError) as e: 
        #     print_lg("(Undetected Mode) Got '{}' when using pre-installed ChromeDriver.".format(type(e).__name__)) 
            print_lg("Downloading Chrome Driver... This may take some time. Undetected mode requires download every run!")
            version_main = get_chrome_major_version()
            driver = uc.Chrome(options=options, version_main=version_main)
    else: driver = webdriver.Chrome(options=options) #, service=Service(executable_path="C:\\Program Files\\Google\\Chrome\\chromedriver-win64\\chromedriver.exe"))
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    return options, driver, actions, wait

# Initialize driver at module load time only for backward compatibility
# (when runAiBot.py is run directly without start.py)
# This is skipped when config.json is present (indicating new flow via start.py)
import os as _os
_should_init = not _os.path.exists("config.json")

if _should_init:
    try:
        options, driver, actions, wait = None, None, None, None
        options, driver, actions, wait = createChromeSession()
    except SessionNotCreatedException as e:
        critical_error_log("Failed to create Chrome Session, retrying with guest profile", e)
        options, driver, actions, wait = createChromeSession(True)
    except Exception as e:
        msg = 'Seems like Google Chrome is out dated. Update browser and try again! \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
        if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
        print_lg(msg)
        safe_alert(msg, "Error in opening chrome")
        try: driver.quit()
        except NameError: exit()
else:
    # When using new config.json flow, these will be set by start.py
    options, driver, actions, wait = None, None, None, None
    
