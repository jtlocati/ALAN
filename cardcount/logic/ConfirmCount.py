from __future__ import annotations
from collections import Counter

class StreakGate:
    def __init__(self, frames: int = 12, ResetFrames: int = 6) -> None:
        self._resetFrames = ResetFrames
        self.frames = frames
        self._counts: Counter = Counter()
        self._streak: Counter = Counter()
        self._missing: Counter=Counter()

    #return confirmed keys from one frame
    def update(self, observed: Counter) -> Counter:
        for key in list(self._counts):
            #card comes, reset missing frames
            if key in observed:
                self._missing[key] = 0
                continue
            self._missing[key] +=1

            if self._streak[key] < self.frames:
                del self._counts[key]
                del self._streak[key]
                del self._missing[key]
            elif self._missing[key] >= self._resetFrames:
                del self._counts[key]
                del self._streak[key]
                del self._missing[key]

        for key, n in observed.items():
            if self._counts.get(key) == n:
                self._streak[key] +=1
            else:
                self._counts[key] = n
                self._streak[key] = 1

        return Counter({k: self._counts[k]for k, s in self._streak.items() if s >= self.frames})

    #keys seen in frame but not confirmed
    def pending(self, observed: Counter) -> Counter:
        return Counter({k: n for k, n in observed.items() if self._streak.get(k, 0) < self.frames})
