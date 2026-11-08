"""Crowd alert state machine (time based, FPS independent)."""
import time
from dataclasses import dataclass


@dataclass
class AlertState:
    active: bool          # ALERT এখন চালু?
    pending: bool         # threshold ছাড়িয়েছে, কিন্তু এখনো দুই সেকেন্ড হয়নি
    elapsed: float        # কতক্ষণ ধরে টানা threshold এর বেশি
    duration: float       # প্রয়োজনীয় সময়


class CrowdAlert:
    def __init__(self, threshold, duration=2.0, clear_delay=0.5):
        self.threshold = threshold
        self.duration = duration
        self.clear_delay = clear_delay
        self.active = False
        self._over_since = None
        self._ok_since = None

    def update(self, count, now=None):
        now = time.monotonic() if now is None else now
        elapsed = 0.0

        if count > self.threshold:
            self._ok_since = None
            if self._over_since is None:
                self._over_since = now
            elapsed = now - self._over_since
            if elapsed >= self.duration:
                self.active = True
        else:
            self._over_since = None
            if self.active:
                if self._ok_since is None:
                    self._ok_since = now
                if now - self._ok_since >= self.clear_delay:
                    self.active = False
                    self._ok_since = None

        pending = (not self.active) and self._over_since is not None
        return AlertState(self.active, pending, elapsed, self.duration)
