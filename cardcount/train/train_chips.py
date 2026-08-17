from pathlib import Path
from ultralytics import YOLO

YMAL_DATA = r"C:\Users\jetlo\onedrive\documents\github\ALAN\cardcount\data/datasets/chips/data.yaml"



def main() -> None:
    model = YOLO("yolo11n.pt")

    model.train(
        data=str(YMAL_DATA), project="runs/chips", name="y11n_640_v1",
        epochs=60, patience=20, batch=-1, 
        imgsz=640, hsv_h=0.0, hsv_s=0.4, hsv_v=0.4, degrees=180.0,fliplr=0.5, flipud=0.5, scale=0.4, mosaic=1.0, close_mosaic=15, mixup=0.0,
        cos_lr=True, seed=0, plots=True
    )
    metrics = model.val(data=str(YMAL_DATA), split="test")
    print(f"test mAP50-95: {metrics.box.map:.4f}")


if __name__ == "__main__":
    main()