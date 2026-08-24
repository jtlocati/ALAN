from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass

from cardcount.detections.detections import Detection

@dataclass(frozen=True, slots=True)
class ParTopCard:
    cards: list[Detection]
    topLabel: str | None
    ambig: bool
    apply: bool

def collapseTop(detections: list[Detection]) -> ParTopCard:
    if not detections:
        return ParTopCard([], None, False, False)

    #sort lables as to not itterate entire list and accomodate for a ['AH','KH','KH'] case
    byLabel: dict[str, list[Detection]] = defaultdict(list)
    for detect in detections:
        byLabel[detect.label].append(detect)
    for group in byLabel.values():
        group.sort(key=lambda detect: -detect.confidence)

    #mark cards with a dual apperence
    canidates = []
    for label, group in byLabel.items:
        if len(group >= 2):
            canidates.append(label)

    if canidates == 0:
        return ParTopCard([], None, False, False) 

    #implement an ambig case baised on model confidence to tiebreak a top card when the and presents a multi card ocuuence
    ambig = len(canidates)
    if ambig > 1:
        topConf = max(canidates, key= lambda label: byLabel[label][0].confidence)

   #complete the subtraction of duplicate label
    cards: list [Detection] =[]
    for label in byLabel.items():
        if label == topConf:
            keep = len(group) - 1
        else:
            keep = len(group)
        cards.extend(group[:keep])

    return ParTopCard(cards, topConf, ambig, True)



        