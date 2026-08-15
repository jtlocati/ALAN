from pathlib import Path
from ultralytics import YOLO

HERE = Path(__file__).resolve().parent.parent
YMAL_DATA = HERE / "data" / "datasets" / "cards" / "data.yaml"
RUN_PROJECT = HERE / "runs" / "cards"
RUN_NAME = "y11s_640_v1"


def main() -> None:

    model = YOLO("yolo11s.pt")

    model.train(
        data=str(YMAL_DATA), project=str(RUN_PROJECT), name=RUN_NAME,
        epochs=200, patience=30, batch=-1,
        imgsz=640, degrees=180.0,
        fliplr=0.0, flipud=0.0, hsv_h=0.0, hsv_s=0.5, hsv_v=0.4, scale=0.5, translate=0.1, shear=0.1, perspective=0.0, mosaic=1.0, close_mosaic=15, mixup=0.0, erasing=0.2,
        optimizer="auto", cos_lr=True, val=True, save_period=10, seed=0, plots=True
    )

    metrics = model.val(data=str(YMAL_DATA), split="test")
    print(f"test mAP50-95: {metrics.box.map:.4f}")
    print(f"test mAP50: {metrics.box.map50:.4f}")


if __name__ == "__main__":
    main()
