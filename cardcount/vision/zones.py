from __future__ import annotations
from dataclasses import dataclass, replace
import cv2
import numpy
from cardcount.detections.detections import Detection

@dataclass(frozen=True, slots=True)
class band:
    name: str
    y0: float
    y1: float


    #define the top and bottom limits for window interp
    def pixels(self, frame_height: int)->tuple[int, int]:
        top = max(0, int(self.y0 * frame_height))
        bottom = min(frame_height, int(self.y1 * frame_height))
        return top, bottom

ROLES: tuple[band, ...] = (band("dealer", 0.00, 0.33), band("pot", 0.33, 0.66), band("player", 0.66, 1.00))

CHIP_BAND = "pot"
CARD_BANDS = ("player", "dealer")
CROP_MARGIN_FRAC = 0.03


#pass var to different contexts, return feaild rather than dict
@dataclass(frozen=True, slots=True)
class TableValues:
    dealer: list[Detection]
    pot: list[Detection]
    player: list[Detection]
    unassigned: list[Detection]


    @property
    def total_cards(self) -> int:
        return len(self.dealer) + len(self.player)

    def __str__(self) -> str:
        return (f"dealer={[d.label for d in self.dealer]} player={[d.label for d in self.player]} pot={len(self.pot)} chips")


def band_for(detection: Detection, bands: tuple[band, ...], frame_height: int) -> str | None:
    _, cent = detection.center
    for zone in bands:
        top, bottom = zone.pixels(frame_height)
        if top <= cent < bottom:
            return zone.name
    return None

#build marjin of error for the attention zones
def crop_band(frame: numpy.ndarray, zone: band, margin: float = CROP_MARGIN_FRAC) -> tuple[numpy.ndarray, int]:
    height = frame.shape[0]
    top, bottom = zone.pixels(height)

    padding = int(margin * height)
    top = max(0, top - padding)
    bottom = min(height, bottom + padding)


    return frame[top:bottom, :], top

def shift(detections: list[Detection], dy: int) -> list[Detection]:
    if dy == 0:
        return detections
    out = []
    for d in detections:
        x1, y1, x2, y2 = d.box
        out.append(replace(d, box=(x1, y1 + dy, x2, y2 + dy)))
    return out


def drawBands(frame: numpy.ndarray, bands: tuple[band, ...] = ROLES) -> None:
    h, w = frame.shape[:2]
    for zone in bands:
        top, bottom = zone.pixels(h)
        cv2.line(frame, (0, top), (w, top), (90, 90, 90), 1, cv2.LINE_AA)
        cv2.putText(frame, zone.name, (8, top + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1, cv2.LINE_AA)
    bottom = bands[-1].pixels(h)[1]
    cv2.line(frame, (0, bottom - 1), (w, bottom - 1), (90, 90, 90), 1, cv2.LINE_AA)
