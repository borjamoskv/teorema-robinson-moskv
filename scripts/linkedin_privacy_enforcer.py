#!/usr/bin/env python3
"""
LinkedIn Privacy Enforcer (Zero-Friction C5-REAL)
Uses the upgraded Darwin_CGEvent_Injector to programmatically enforce privacy settings
in the background without stealing user focus.
"""

import sys
import time
import subprocess
from typing import Dict, Any

# Append the skill scripts path
sys.path.append("/Users/borjafernandezangulo/.gemini/config/skills/Darwin_CGEvent_Injector/scripts")
try:
    from ui_maestro import UIMaestro
except ImportError:
    print("Error: Darwin_CGEvent_Injector skill not found or incomplete.")
    sys.exit(1)

def navigate_brave_to(url: str) -> None:
    """Uses AppleScript to navigate Brave's active tab to the target settings page."""
    cmd = f'tell application "Brave Browser" to set URL of active tab of front window to "{url}"'
    subprocess.run(["osascript", "-e", cmd], capture_output=True)
    time.sleep(4) # Allow page load

def enforce_setting(url: str, element_title: str) -> Dict[str, Any]:
    """Navigates and clicks the element using zero-friction coordinate mapping."""
    print(f"[PRIVACY-ENFORCER] Targeting: {element_title} at {url}")
    navigate_brave_to(url)
    
    maestro = UIMaestro()
    try:
        # Perform logical finding and physical click injection O(1)
        res = maestro.click_element_by_title_zero_friction(element_title, "Brave Browser")
        print(f"[PRIVACY-ENFORCER] Success: {res}")
        return res
    except Exception as e:
        print(f"[PRIVACY-ENFORCER] Failed to toggle {element_title}: {e}")
        return {"status": "failed", "error": str(e)}

def main():
    print("=== STARTING ZERO-FRICTION PRIVACY ENFORCEMENT ===")
    
    # 1. Enforce "Modo privado" (anonymity visiting profiles)
    enforce_setting(
        "https://www.linkedin.com/mypreferences/d/profile-viewing-options",
        "Modo privado"
    )
    
    # 2. Enforce "Difundir cambios de actividad" (don't alert network of updates)
    enforce_setting(
        "https://www.linkedin.com/mypreferences/d/settings/notify-network-for-updates",
        "No" # Usually toggles a switch to "No"
    )
    
    print("=== PRIVACY ENFORCEMENT RUN COMPLETE ===")

if __name__ == "__main__":
    main()
