from pathlib import Path

import cv2

from cardcount.detections.detectors import Detector
from cardcount.metrics.eval import BJ_COUNTS, rankCards
from cardcount.vision.camera import OpenCam, draw
from cardcount.vision.table import analizeFrames
from cardcount.vision.zones import drawBands
from cardcount.logic.ConfirmCount import StreakGate
from collections import Counter


CHIP_WEIGHT = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\chips_best.pt"
CARD_WEIGHT = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\cards_best.pt"

CAM = 1
IMGSZ = 640
DEVICE = "cpu"
CARD_CONF = 0.25
CHIP_CONF = 0.50
CONF_FRAMES = 4

def NormaliseChip(raw: str) -> str:
    return raw.strip().lower().replace(" chip", "")


DENOMINATIONS = {"white": 1, "red": 5, "blue": 10, "green": 25, "black": 100}

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

            observed = Counter()
            for d in view.dealer:
                observed[("dealer", d.label)] += 1
            for d in view.player:
                observed[("player", d.label)] += 1

            confirmed = gate.update(observed)

            dealerCards = sorted(lbl for (role, lbl), n in confirmed.items() for _ in range(n) if role == "dealer")
            playerCards = sorted(lbl for (role, lbl), n in confirmed.items() for _ in range(n) if role == "player")

            dealerCount = sum(BJ_COUNTS.get(rankCards(l), 0) for l in dealerCards)
            playerCount = sum(BJ_COUNTS.get(rankCards(l), 0) for l in playerCards)

            potTotal = sum(DENOMINATIONS.get(NormaliseChip(d.label), 0) for d in view.pot)

            if view.unassigned:
                print(f"  !! cards in the betting band: "
                      f"{[d.label for d in view.unassigned]}")

            print(f"D {dealerCards} | P {playerCards} | "
                  f"pot >= ${potTotal} | hi-lo {dealerCount + playerCount:+d}")

            if showBands:
                drawBands(frame)

            draw(frame, view.dealer, colour=(0, 225, 0))
            draw(frame, view.player, colour=(0, 225, 0))
            draw(frame, view.pot, colour=(255, 200, 0))
            draw(frame, view.unassigned, colour=(0, 140, 255))

            cv2.putText(frame, f"pot >= ${potTotal} DEALER HAND {dealerCards} | PLAYER HAND {playerCards} ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
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
