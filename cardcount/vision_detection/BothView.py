import time
from collections import Counter
import cv2
from cardcount.detections.detectors import Detector
from cardcount.vision.camera import draw, OpenCam, sream
#Whateva, whateva, i do what i want
imgSZ = 640
DEV = "cpu"
CAM = 1


def main() -> None:
    cards = Detector(r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\cards_best.pt", imgsz=imgSZ, device=DEV)
    chips = Detector(f"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\chips_best.pt", imgsz=imgSZ, device=DEV)

    if cards is not None:
        print(f"{'='*6}CARDS LOADED: ATTR_NUM = {len((cards.names))}{'='*6}")
    if chips is not None:
        print(f"{'='*6}CHIPS LOADED: ATTR_NUM = {len((chips.names))}{'='*6}")

    else:
        raise AttributeError(f"==ERROR LOADING CARDS:\n CARDS ATTR_NUM = {len(cards.names)}\nCHIPS ATTR_NUM: {len(chips.names)}")

    camera = OpenCam(source=CAM, width=1280, height=720)
    cards.warmup(camera.height, camera.width)
    chips.warmup(camera.height, camera.width)

    fps, last = 0.0, time.perf_counter()

    try:
        while True:
            frame = camera.read()
            if frame is None:
                time.sleep(0.005)
                continue

            card_detect = cards.detect(frame, conf=0.25)
            chip_detect = chips.detect(frame, conf=0.5)

            present = sorted({d.label for d in card_detect})
            chip_counts = Counter(d.label for d in chip_detect)

            draw(frame, card_detect, colour=(0, 255, 0))
            draw(frame, chip_detect, colour=(255, 200, 0))

            now = time.perf_counter()

            fps = 0.9 * fps + 0.1 / max(1e-6, now - last)
            last = now

            cv2.putText(frame, f"{fps:4.1f} fps | {len(present)} cards | {sum(chip_counts.values())} chips", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("ALAN full detect build", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()