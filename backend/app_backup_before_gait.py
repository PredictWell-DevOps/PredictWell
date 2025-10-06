# ruff: noqa
"""
Backup file kept only for historical reference.
This file is not used by the running application or tests.
"""

from __future__ import annotations

# NOTE:
# We intentionally keep this as a minimal, no-side-effects module so that
# CI will not lint/fail on old code while we preserve the backup in the repo.
# The real app lives in `backend/app.py`.

# If you ever need to run something from here locally, you can put it under a
# `if __name__ == "__main__":` guard. Nothing is executed on import.
if __name__ == "__main__":
    print("This is a backup file; the live FastAPI app is backend/app.py.")
