from typing import Dict, Optional, Any
from enum import Enum
from datetime import datetime

class SessionState(Enum):
    IDLE = "idle"
    EDITING_CASE = "editing_case"

class SessionManager:
    def __init__(self):
        # In-memory storage for now. For production, use Redis.
        self._sessions: Dict[int, Dict[str, Any]] = {}

    def get_session(self, user_id: int) -> Dict[str, Any]:
        if user_id not in self._sessions:
            self._sessions[user_id] = {
                "state": SessionState.IDLE,
                "active_case_id": None,
                "last_interaction": datetime.now()
            }
        return self._sessions[user_id]

    def set_active_case(self, user_id: int, case_id: str):
        session = self.get_session(user_id)
        session["state"] = SessionState.EDITING_CASE
        session["active_case_id"] = case_id
        session["last_interaction"] = datetime.now()

    def clear_session(self, user_id: int):
        if user_id in self._sessions:
            self._sessions[user_id] = {
                "state": SessionState.IDLE,
                "active_case_id": None,
                "last_interaction": datetime.now()
            }

session_manager = SessionManager()
