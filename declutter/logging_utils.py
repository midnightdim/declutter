import logging
import os
from declutter.config import LOG_FILE

def _refresh_log_file_handler(mode="a+"):
    """Detach the FileHandler for LOG_FILE (if any) and attach a fresh one with same formatter."""
    root = logging.getLogger()
    old = None
    for h in list(root.handlers):
        if isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == os.path.abspath(LOG_FILE):
            try:
                h.flush()
            except Exception:
                pass
            try:
                h.close()
            except Exception:
                pass
            old = h
            root.removeHandler(h)
            break
    if old:
        fmt = old.formatter or logging.Formatter("%(asctime)-15s %(levelname)-8s %(message)s")
        new_fh = logging.FileHandler(filename=LOG_FILE, encoding="utf-8", mode=mode)
        new_fh.setFormatter(fmt)
        root.addHandler(new_fh)