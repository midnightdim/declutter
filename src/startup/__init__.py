import sys
if sys.platform.startswith("win"):
    from .windows import is_startup_enabled as is_enabled, enable_startup as enable, disable_startup as disable
elif sys.platform == "darwin":
    from .macos import is_startup_enabled as is_enabled, enable_startup as enable, disable_startup as disable
else:
    def is_enabled() -> bool: return False
    def enable() -> bool: return False
    def disable() -> bool: return False
