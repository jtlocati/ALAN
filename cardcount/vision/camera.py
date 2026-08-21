import threading
import time
from collections.abc import Iterator
import cv2
import numpy
from cardcount.detections.detections import Detection
from cardcount.detections.detectors import Detector

class frameGrabbber:
    def __init__(self, source: int | str = 0, width: int = 1280, height: int = 720):
        backend = cv2.CAP_ANY
        if isinstance(source, int):
            backend = cv2.CAP_DSHOW

        self.cap = cv2.VideoCapture(source, backend)
        if not self.cap.isOpened():
            raise RuntimeError(f"COULD NOT OPEN CAMERA SOURCE @ {source}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self._frame: numpy.ndarray | None = None
        self._lock = threading.Lock()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while self._running:
            ok, frame  = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue
            with self._lock:
                self._frame = frame

    def read(self) -> numpy.ndarray | None:
        with self._lock:
            if (self._frame is None):
                return None
            return self._frame.copy()

    def release(self) -> None:
        self._running = False
        self._thread.join(timeout=1.0)
        self.cap.release()

def OpenCam(source: int | str = 0, width: int =1280, height: int=720) -> frameGrabbber:
    return frameGrabbber(source, width, height)


def sream(detector: Detector, source: int | str = 0, conf: float = 0.5, width: int = 1280, height: int = 720,) -> Iterator[tuple[numpy.ndarray, list[Detection]]]:
    grabber = frameGrabbber(source, width, height)
    detector.warmup(grabber,height, grabber.width)

    try:
        while True:
            frame = grabber.read()
            if frame is None:
                time.sleep(0.005)
                continue
            yield frame, detector.detect(frame, conf=conf)
    finally:
        grabber.release()

def draw(frame: numpy.ndarray, detections: list[Detection], colour=(0, 255, 0)) -> None:
    for d in detections:
        x1, y1, x2, y2 = d.int_box()
        cv2.rectangle(frame, (x1, y1), (x2, y2), colour, 2)
        cv2.putText(frame, f"{d.label} {d.confidence:.2f}", (x1, max(12, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1, cv2.LINE_AA)