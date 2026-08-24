from __future__ import annotations
from collections import Counter

class StreakGate:
    def __init__(self, frames: int = 12) -> None:
        self.frames = frames
        self._counts: Counter = Counter()
        self._streak: Counter = Counter()

    #return confirmed keys from one frame
    def update(self, observed: Counter) -> Counter:
        for key in list(self._streak):
            if key not in observed:
                self._streak[key] = 0
                self._counts[key] = 0

        for key, n in observed.items():
            if self._counts.get(key) == n:
                self._streak[key] +=1
            else:
                self._counts[key] = n
                self._counts[key] = 1

        return Counter({k: self._counts[k]for k, s in self._streak.items() if s >= self.frames})

    #keys seen in frame but not confirmed
    def pending(self, observed: Counter) -> Counter:
        return Counter({k: n for k, n in observed.items() if self._streak.get(k, 0) < self.frames})


    