import platform
import re
import os

def detect_os_and_browser(user_agent):
    """
    Detects the operating system and browser based on the user agent string.
    """
    os_name = platform.system()
    browser_name = "Unknown"

    # Detect browser from user agent
    if "Chrome" in user_agent:
        browser_name = "Chrome"
    elif "Firefox" in user_agent:
        browser_name = "Firefox"
    elif "Safari" in user_agent and "Chrome" not in user_agent:
        browser_name = "Safari"
    elif "Edge" in user_agent:
        browser_name = "Edge"
    elif "Brave" in user_agent:
        browser_name = "Brave"

    return os_name, browser_name

def get_browser_history_path(os_name, browser_name):
    """
    Returns the path to the browser's history database based on the OS and browser.
    """
    if os_name == "Windows":
        if browser_name == "Chrome":
            return os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
        elif browser_name == "Edge":
            return os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History")
        elif browser_name == "Brave":
            return os.path.expanduser("~\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\History")
    elif os_name == "Darwin":  # macOS
        if browser_name == "Safari":
            return os.path.expanduser("~/Library/Safari/History.db")
    elif os_name == "Linux":
        if browser_name == "Chrome":
            return os.path.expanduser("~/.config/google-chrome/Default/History")
        elif browser_name == "Brave":
            return os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/History")
    return None

