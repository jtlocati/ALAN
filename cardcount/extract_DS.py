import os
from pathlib import Path
from roboflow import Roboflow
import yaml

DATASET_LOCATION = Path(os.environ.get("ALAN_DS", "data/datasets"))

DATASET_LOCATION.mkdir(parents=True, exist_ok=True)

TARGETS = (("augmented-startups", "playing-cards-ow27d", 4, "cards"), ("jvdm", "pokerchips-tltea", 7, "chips"),)

KEY = os.environ.get("ROBO_API_KEY")

def DownloadData() -> dict[str, Path]:
    if not KEY:
        raise KeyError("ROBO key not set gng")

    ROBO = Roboflow(api_key=KEY)
    paths: dict[str, Path] = {}

    for workspace, project_slug, version, name in TARGETS:
        desitination = DATASET_LOCATION / name
        if (desitination / "data.yaml").exists():
            print(f"{'='*6}{name} FOUND AT: {desitination}, SKIPPING DOWNLOAD {'='*6}")
            paths[name] = desitination
            continue

        print(f"{'='*6} adding to: {workspace}/{project_slug}: v{version}{'='*6}")
        project = ROBO.workspace(workspace).project(project_slug)
        versionOP = project.version(version)

        boop = True

        try:
            dataset = versionOP.download("Yolov11", location=str(desitination))
            print(f"{'='*6} saved to => {paths[name]} AS YOLOv11 {'='*6}")
            boop = False
        except Exception as exception:
            print(f"{'='*6}YOLOv11 failed, falling back to YOLOv8")
            dataset = versionOP.download("yolov8", location=str(desitination))

        paths[name] = Path(dataset.location)
        if boop:
            print(f"{name.upper()} => {paths[name]} AS YOLOv8")
        else:
            print(f"{name.upper()} => {paths[name]} AS YOLOv11")

    return paths

def DTYMAL(dataset: Path) -> None:
    ymal_path = dataset / "data.yaml"
    config = yaml.safe_load(ymal_path.read_text())

    for split in ("train", "val", "test"):
        if split in config:
            config[split] = str((dataset / split / "images").resolve())

    ymal_path.write_text(yaml.safe_dump(config, sort_keys=False))
    print(f"{dataset.name} yaml safe path complete")
    print(f"{dataset.name} => {len(config.get('names', []))} classes: {config.get('names')}")


if __name__ == "__main__":
    for name, path in DownloadData().items():
        DTYMAL(path)