from pathlib import Path
import numpy
from ultralytics import YOLO
from detections import Detection

class Detector:
    def __init__(self, weights: str | Path, imgsz: int = 640, device: str | int = "cpu", half: bool = False) -> None:
        weights = Path(weights)
        if weights.is_file() is None:
            raise FileNotFoundError(f"{weights} is not a valid weights file")

        self.model = YOLO(str(weights))
        self.imgsz = imgsz
        self.device = device
        self.half = half

        #read labels from model
        self.names: dict[int, str] = dict(self.model.names)

    def warmup(self, height: int = 480, width: int = 640) -> None:
        blank = numpy.zeros((height, width, 3), dtype=numpy.unit8)
        self.model.predict(blank, imgsz=self.imgsz, device=self.device, half=self.half, verbose=False)


    def detect(self, frame:numpy.ndarray, conf: float = 0.5) -> list[Detection]:
        results = self.model.predict(
            frame, imgsz=self.imgsz, conf=conf,
            device=self.device, half=self.half,
            verbose=False,   # otherwise ultralytics prints a line per frame
        )

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return []

        XYsqrt = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        clss = boxes.cls.cpu().numpy().astype(int)

        return [
            Detection(
                label=self.names[int(c)],
                confidence=float(p),
                box=(float(x1), float(y1), float(x2), float(y2)),
            )
            for (x1, y1, x2, y2), p, c in zip(XYsqrt, confs, clss)
        ]