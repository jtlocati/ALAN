from __future__ import annotations
from dataclasses import dataclass, replace

Box = tuple[float, float, float, float]

@dataclass(frozen=True, slots=True)
class Detection:

    label: str
    confidence: float
    box: Box
    trackId: int | None = None


    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.box
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def width(self) -> float:
        return self.box[2] - self.box[0]

    @property
    def height(self) -> float:
        return self.box[3] - self.box[1]

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.height)

    def withTrackId(self, trackId: int | None) -> "Detection":
        return replace(self, trackId=trackId)
    
    def int_box(self) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = self.box
        return (int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)))

    def __str__(self) -> str:
        tidy = ""
        if self.trackId is not None:
            tidy = (f"#{self.trackId}")
        cx, cy = self.center
        return f"{self.label}{tidy} {self.confidence:.2f} @({cx:.0f},{cy:.0f})"

