"""
Utils package for Marxnager bot.

This package combines utilities from:
- src/utils.py (legacy utilities)
- src/utils/retry.py (retry decorators)
- src/utils/monitoring.py (monitoring utilities)

To maintain backward compatibility, we re-export the legacy utils here.
"""

# Import legacy utilities from the utils.py file
# We need to import it as a module since src/utils.py exists
import sys
from pathlib import Path

# Add parent directory to path to import utils.py
_utils_path = Path(__file__).parent.parent / "utils.py"

# Load the utils module
import importlib.util
spec = importlib.util.spec_from_file_location("_legacy_utils", _utils_path)
_legacy_utils = importlib.util.module_from_spec(spec)
sys.modules["_legacy_utils"] = _legacy_utils
spec.loader.exec_module(_legacy_utils)

# Re-export for backward compatibility
ProgressTracker = _legacy_utils.ProgressTracker
generate_case_id = _legacy_utils.generate_case_id
get_logs = _legacy_utils.get_logs
RollbackManager = _legacy_utils.RollbackManager
send_progress_message = _legacy_utils.send_progress_message
update_progress_message = _legacy_utils.update_progress_message

__all__ = [
    "ProgressTracker",
    "generate_case_id",
    "get_logs",
    "RollbackManager",
    "send_progress_message",
    "update_progress_message",
]
