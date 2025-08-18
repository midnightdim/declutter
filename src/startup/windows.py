# Stub module for Windows startup management.
#
# Why a stub:
# - Windows startup is controlled by the installer (e.g., Startup Apps UI).
# - To avoid conflicts and state desynchronization, the app does NOT
#   manipulate startup entries on Windows.
# - This stub preserves a consistent cross-platform API without changing system state.

def is_startup_enabled() -> bool:
    # We do not read OS state here to avoid implying app-side control.
    # The effective startup status should be managed by the Windows "Startup Apps" UI.
    return False

def enable_startup() -> bool:
    # No-op on Windows by design (installer/OS manages startup).
    return False

def disable_startup() -> bool:
    # No-op on Windows by design (installer/OS manages startup).
    return False
