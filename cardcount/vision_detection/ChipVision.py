from collections import Counter
from pathlib import Path
import cv2
from cardcount.vision.camera import draw, sream
from cardcount.detections.detectors import Detector


PROJECT_ROOT = Path(__file__).resolve().parent.parent

#include absolute weight path
WEIGHTS = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\chips_best.pt"

CONF = 0.5
IMGsz = 640
CAM = 1

CHIP_NAMES = {"black chip": "black", "blue chip": "blue", "green chip": "green", "red chip": "red", "white chip": "white"}
DENOMINATIONS = {"white": 1, "red": 5, "blue": 10, "green": 25, "black": 100}

def canolitical(raw: str) -> str:
    return CHIP_NAMES.get(raw.strip().lower(), raw.strip().lower())


def main():
    detector = Detector(WEIGHTS, imgsz=IMGsz, device="cpu")
    if detector is not None:
        print(f"running chip model raw: {detector.names.values }")

    for frame, detect in sream(detector, source=CAM, conf=CONF):
        counts = Counter(canolitical(d.label) for d in detect)
        total = sum(DENOMINATIONS.get(colour, 0) * n for colour, n in counts.items())

        unknown = [un for un in counts if un not in DENOMINATIONS]

        if unknown is None or unknown == "":
            print(f"unmapped chip labels: {unknown}")

        print(f"{dict(counts)}  >= ${total}")

        draw(frame, detect, colour=(255, 200, 0))
        cv2.putText(frame, f">= ${total}, ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.imshow("ALAN - chips", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    