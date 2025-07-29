from enum import Enum, auto
import threading

class AvatarState(Enum):
    IDLE = auto()
    TALKING = auto()
    THINKING = auto()

class StateManager:
    def __init__(self):
        self._current_state = AvatarState.IDLE
        self._state_lock = threading.Lock()

    @property
    def current_state(self):
        with self._state_lock:
            return self._current_state

    def set_state(self, new_state):
        with self._state_lock:
            self._current_state = new_state