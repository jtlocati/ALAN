from cardcount.detections.detections import Detection
from cardcount.detections.detectors import Detector
from cardcount.vision.zones import (ROLES, CHIP_BAND, band, TableValues, band_for, crop_band, shift)
import numpy
from collections import defaultdict
from cardcount.logic.TopCardPairity import collapseTop, conf, stripSuite

SUIT_PROBE = True

def suitProbe(detections: list[Detection]) -> None:
    seen: dict[str, set[str]] = defaultdict(set)
    for d in detections:
        seen[d.label[:-1]].add(d.label[-1])
    for rank, suits in seen.items():
        if len(suits) > 1:
            print(f"  ?? {rank}: suits disagree {sorted(suits)}")

def analizeFrames(frame: numpy.ndarray, cardModel: Detector, chipmodel: Detector, card_conf: float = 0.25, chip_conf = 0.50, bands: tuple[band, ...] = ROLES) -> TableValues:
    frameHeight = frame.shape[0]
    #detection: list[Detection]

    #run card model on whole frame
    cardDetection = cardModel.detect(frame, conf=card_conf)

    if SUIT_PROBE:
        suitProbe(cardDetection)

    buckets: dict[str, list[Detection]] = {b.name: [] for b in bands}
    for detection in cardDetection:
        name = band_for(detection, bands, frameHeight)
        if name is not None:
            buckets[name].append(detection)

    for name in buckets:
        buckets[name] = stripSuite(conf(buckets[name]))


    #crop fed image according to the params set in zones then run chip model

    ChipBand = next(b for b in bands if b.name == CHIP_BAND)
    Az, Yoffset = crop_band(frame, ChipBand)
    chipDetections = chipmodel.detect(Az, conf=chip_conf)
    chipDetections = shift(chipDetections, Yoffset)

    chipDetections = [d for d in chipDetections if band_for(d, bands, frameHeight) == CHIP_BAND]

    return TableValues(
        dealer=buckets["dealer"],
        player=buckets["player"],
        pot=chipDetections,
        unassigned=buckets[CHIP_BAND],
    )
