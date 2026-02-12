# macOS implementation using a per-user LaunchAgent to start at login.

import os
import sys
import plistlib
import subprocess
from pathlib import Path

AGENT_LABEL = "com.declutter.autostart"
AGENT_PLIST = Path.home() / "Library" / "LaunchAgents" / f"{AGENT_LABEL}.plist"
_IS_POSIX = os.name == "posix"

def _app_executable_path() -> str:
    # In a bundled app, sys.executable points to DeClutter.app/Contents/MacOS/DeClutter
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(sys.argv[0])

def _desired_plist(exe_path: str) -> dict:
    return {
        "Label": AGENT_LABEL,
        "Program": exe_path,
        "RunAtLoad": True,
        "KeepAlive": False,
        "ProcessType": "Interactive",
    }

def _user_domain() -> str:
    # Guard getuid so linting on Windows doesn't fail.
    return f"gui/{os.getuid()}" if _IS_POSIX else ""

def is_startup_enabled() -> bool:
    if not AGENT_PLIST.exists():
        return False
    try:
        with AGENT_PLIST.open("rb") as f:
            data = plistlib.load(f)
        exe = data.get("Program") or ""
        return os.path.normpath(exe) == os.path.normpath(_app_executable_path())
    except Exception:
        return False

def enable_startup() -> bool:
    try:
        exe = _app_executable_path()
        AGENT_PLIST.parent.mkdir(parents=True, exist_ok=True)
        with AGENT_PLIST.open("wb") as f:
            plistlib.dump(_desired_plist(exe), f)

        if _IS_POSIX:
            # Modern launchctl (best-effort)
            cmd = ["launchctl", "bootstrap", _user_domain(), str(AGENT_PLIST)]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode != 0:
                # Fallback legacy load
                subprocess.run(["launchctl", "load", str(AGENT_PLIST)],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False

def disable_startup() -> bool:
    ok = True
    try:
        if _IS_POSIX:
            subprocess.run(["launchctl", "bootout", _user_domain(), f"{_user_domain()}/{AGENT_LABEL}"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["launchctl", "unload", str(AGENT_PLIST)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        ok = False
    try:
        if AGENT_PLIST.exists():
            AGENT_PLIST.unlink()
    except Exception:
        ok = False
    return ok
