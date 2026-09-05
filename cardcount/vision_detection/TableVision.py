from pathlib import Path

import cv2

from cardcount.detections.detectors import Detector
from cardcount.metrics.eval import BJ_COUNTS, rankCards
from cardcount.vision.camera import OpenCam, draw
from cardcount.vision.table import analizeFrames
from cardcount.vision.zones import drawBands
from cardcount.logic.ConfirmCount import StreakGate
from collections import Counter
from dataclasses import dataclass


CHIP_WEIGHT = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\chips_best.pt"
CARD_WEIGHT = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\cards_best.pt"

CAM = 1
IMGSZ = 640
DEVICE = "cpu"
CARD_CONF = 0.25
CHIP_CONF = 0.50
CONF_FRAMES = 4

@dataclass(frozen=True, slots=True)
class TableReading:
    PlayerCards: list[str]
    DealerCards: list[str]
    runningCount: int
    potTotal: int
    chipColors: list[str]


def NormaliseChip(raw: str) -> str:
    return raw.strip().lower().replace(" chip", "")


DENOMINATIONS = {"white": 1, "red": 5, "blue": 10, "green": 25, "black": 100}

def readTable(view, gate) -> TableReading:
    observed = Counter()
    #find cards per person + the count it holds
    for detection in view.dealer:
        dealerKey = ("dealer", detection.label)
        #Recall the given card @ location [key] include an additional +1 trakcer per carrd instance 
        observed[dealerKey] = observed[dealerKey] + 1

    for detection in view.player:
        playerKey = ("player", detection.label)
        observed[playerKey] = observed[playerKey] +1

    confirmedCards = gate.update(observed)

    dealer_cards = []
    player_cards = []

    for roleLabel, cardCount in confirmedCards.items():
        role = roleLabel[0]
        card = roleLabel[1]

        for _ in range(cardCount): 
            if role == "dealer":
                dealer_cards.append(card)
            else:
                player_cards.append(card)

    dealer_cards.sort()
    player_cards.sort()

    #find count
    runnning_count = 0

    for card in dealer_cards:
        dealerRank = rankCards(card)
        runnning_count = runnning_count + BJ_COUNTS.get(dealerRank, 0)

    for label in dealer_cards:
        playerRank = rankCards(card)
        runnning_count = runnning_count + BJ_COUNTS(playerRank, 0)


    #find pot
    potTotal = 0
    chipColors = []


    for detection in view.pot:
        color = NormaliseChip(detection.label)
        chipColors.append(color)

        potTotal = potTotal + DENOMINATIONS.get(color,0)

    return TableReading(
        DealerCards=dealer_cards,
        PlayerCards=player_cards,
        runningCount=runnning_count,
        potTotal=potTotal,
        chipColors=chipColors
    )


def main():
    cardModel = Detector(CARD_WEIGHT, IMGSZ, DEVICE)
    chipModel = Detector(CHIP_WEIGHT, IMGSZ, DEVICE)
    print(f"cards: {len(cardModel.names)} classes | chips: {len(chipModel.names)} classes")
    if len(cardModel.names) != 52:
        raise ValueError(f"expected 52 card classes, got {len(cardModel.names)}")

    cam = OpenCam(source=CAM)
    cardModel.warmup(cam.height, cam.width)
    chipModel.warmup(cam.height, cam.width)

    showBands = True
    gate = StreakGate(CONF_FRAMES)

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            view = analizeFrames(frame, cardModel, chipModel, CARD_CONF, CHIP_CONF)

            reading = readTable(view, gate)
            
            if view.unassigned:
                print(f"  !! cards in the betting band: "
                      f"{[d.label for d in view.unassigned]}")

            print(f"D {reading.DealerCards} | P {reading.PlayerCards} | "
                  f"pot >= ${reading.potTotal} | hi-lo {reading.runningCount:+d}")

            if showBands:
                drawBands(frame)

            draw(frame, view.dealer, colour=(0, 225, 0))
            draw(frame, view.player, colour=(0, 225, 0))
            draw(frame, view.pot, colour=(255, 200, 0))
            draw(frame, view.unassigned, colour=(0, 140, 255))

            cv2.putText(frame, f"pot >= ${reading.potTotal} DEALER HAND {reading.DealerCards} | PLAYER HAND {reading.PlayerCards} ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("ALAN - table", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("z"):
                showBands = not showBands
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
