from pathlib import Path
import cv2
from cardcount.vision.camera import draw, sream
from cardcount.detections.detectors import Detector
from cardcount.metrics.eval import BJ_COUNTS, rankCards

ROOT = Path(__file__).resolve().parents[2]
WEIGHTS = ROOT / "models" / "cards_best.pt"

imgsz = 640
device = "cpu"
Conf=0.25
CAM=1

showInfo = None

def main() -> None:
    detect = Detector(WEIGHTS, imgsz, device)
    print(f"{'='*10}Running CARD model with weights{'='*10}\n {detect.names}")

    if (len(detect.names)!= 52):
        raise ValueError("cannot retiece all classes")

    for frame, detections in sream(detect, source=CAM, conf=Conf):
        present_set = set()

        for d in detections:
            present_set.add(d.label)

        present = sorted(present_set)


        frame_count = 0

        for lbl in present:
            rank = rankCards(lbl)
            parsed_label = rankCards(lbl)
            first_value = parsed_label[0]

            value = BJ_COUNTS.get(first_value, 0)

            frame_count += BJ_COUNTS.get(rank, 0)
    
        print(f"{len(detections):2d} det | {len(present):2d} distinct | frame Hi-Lo {frame_count:+d} | {present}")

        draw(frame, detections, colour=(0, 225, 0))
        cv2.putText(frame, f"CARDS: {present}", (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 225, 255), 2)
        cv2.imshow(f"ALAN CARDS", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()