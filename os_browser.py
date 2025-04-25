import platform
import re

def detect_os_and_browser(user_agent):
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
print(detect_os_and_browser("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
" (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"))  # Example user agent string