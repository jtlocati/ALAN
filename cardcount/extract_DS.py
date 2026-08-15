import os
from pathlib import Path
from roboflow import Roboflow
import yaml

HERE = Path(__file__).resolve().parent
DATASET_LOCATION = Path(os.environ.get("ALAN_DS", HERE / "data" / "datasets"))

DATASET_LOCATION.mkdir(parents=True, exist_ok=True)

TARGETS = (
    ("augmented-startups", "playing-cards-ow27d", 4, "cards"),
    ("jvdm", "pokerchips-tltea", 7, "chips"),
)

KEY = os.environ.get("ROBO_API_KEY")

DETECTION_TYPES = {"object-detection"}

SPLIT_DIRS = {
    "train": ("train",),
    "val": ("valid", "val"),
    "test": ("test",),
}


def is_stale(destination: Path, project_slug: str, version: int) -> bool:
    yaml_path = destination / "data.yaml"
    if not yaml_path.exists():
        return True
    try:
        config = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return True
    meta = config.get("roboflow") or {}
    return meta.get("project") != project_slug or int(meta.get("version", -1)) != version


def preflight(ROBO: Roboflow, workspace: str, project_slug: str, version: int):
    project = ROBO.workspace(workspace).project(project_slug)

    ptype = getattr(project, "type", "<unknown>")
    print(f"{'='*6} {workspace}/{project_slug}: type={ptype} classes={getattr(project, 'classes', '<n/a>')}")

    if ptype not in DETECTION_TYPES:
        raise SystemExit(
            f"{workspace}/{project_slug} is a '{ptype}' project, not object-detection. "
            f"It has no bounding boxes and cannot be exported in a YOLO detection format."
        )

    available = []
    for v in project.versions():
        try:
            available.append(int(str(v.id).split("/")[-1]))
        except ValueError:
            continue

    if available and version not in available:
        raise SystemExit(
            f"{workspace}/{project_slug} has no version {version}. Available: {sorted(available)}"
        )

    return project.version(version)


def DownloadData() -> dict[str, Path]:
    if not KEY:
        raise KeyError("ROBO key not set gng")

    ROBO = Roboflow(api_key=KEY)
    paths: dict[str, Path] = {}

    for workspace, project_slug, version, name in TARGETS:
        desitination = DATASET_LOCATION / name

        if not is_stale(desitination, project_slug, version):
            print(f"{'='*6}{name} FOUND AT: {desitination}, SKIPPING DOWNLOAD {'='*6}")
            paths[name] = desitination
            continue

        if (desitination / "data.yaml").exists():
            raise SystemExit(
                f"{desitination} holds a different dataset than {project_slug} v{version}. "
                f"Delete or rename that folder, then re-run."
            )

        print(f"{'='*6} adding to: {workspace}/{project_slug}: v{version} {'='*6}")
        versionOP = preflight(ROBO, workspace, project_slug, version)

        dataset = versionOP.download("yolov11", location=str(desitination))
        paths[name] = Path(dataset.location)
        print(f"{name.upper()} => {paths[name]} AS YOLOv11")

    return paths


def DTYMAL(dataset: Path) -> None:
    ymal_path = dataset / "data.yaml"
    config = yaml.safe_load(ymal_path.read_text(encoding="utf-8"))

    for split, candidates in SPLIT_DIRS.items():
        if split not in config:
            continue
        for folder in candidates:
            images = dataset / folder / "images"
            if images.exists():
                config[split] = str(images.resolve())
                break
        else:
            print(f"!! {dataset.name}: no folder for split '{split}' among {candidates}")

    ymal_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    print(f"{dataset.name} yaml safe path complete")
    print(f"{dataset.name} => {len(config.get('names', []))} classes: {config.get('names')}")


if __name__ == "__main__":
    for name, path in DownloadData().items():
        DTYMAL(path)
