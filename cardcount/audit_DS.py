import sys
from collections import Counter
from pathlib import Path
import yaml
from PIL import Image


def audit(dataset: Path, sample_img: int = 300) -> None:
    config = yaml.safe_load((dataset / "data.yaml").read_text(encoding="utf-8"))

    names = config["names"]
    if isinstance(names, dict):
        names = [names[i] for i in sorted(names)]
    print(f"{'='*6}{dataset.name}{'='*6}")
    print(f"classes: {len(names)}: {names}")

    counts: Counter[str] = Counter()
    widths: list[float] = []
    height: list[float] = []

    labels_dir = dataset / "train" / "labels"
    if not labels_dir.is_dir():
        print(f"!! no label directory at {labels_dir}")
        return

    files_labels = sorted(labels_dir.glob("*.txt"))
    print(f"{'='*6} Train Label Files: {len(files_labels)}")
    if not files_labels:
        print(f"!! no .txt label files in {labels_dir}")
        return

    for lf in files_labels:
        for line in lf.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue

            contrls = int(parts[0])
            if contrls < 0 or contrls >= len(names):
                continue

            w, h = float(parts[3]), float(parts[4])
            counts[names[contrls]] += 1
            widths.append(w)
            height.append(h)

    total = sum(counts.values())
    print(f"total boxes: {total}   mean per image: {total / max(1, len(files_labels)):.1f}")

    if not counts:
        print("!! no boxes parsed from any label file")
        return

    print("rarest 8")
    for name, n in counts.most_common()[-8:]:
        print(f"{name} : {n:>5}")
    print("common 8")
    for name, n in counts.most_common(8):
        print(f"{name} => {n:>5}")

    missing_labels = [n for n in names if counts[n] == 0]
    print(f"missing classes: {missing_labels}")

    ratio = max(counts.values()) / max(1, min(counts.values()))
    print(f"imbalance ratio: {ratio:.1f}x")

    img_dir = dataset / "train" / "images"
    if not img_dir.is_dir():
        print(f"!! no image directory at {img_dir}")
        return

    img_files = [p for p in sorted(img_dir.iterdir()) if p.is_file()][:sample_img]
    if not img_files:
        print(f"!! no images in {img_dir}")
        return

    sizes: Counter[tuple[int, int]] = Counter()
    for p in img_files:
        try:
            with Image.open(p) as im:
                sizes[im.size] += 1
        except Exception:
            continue

    if not sizes:
        print(f"!! could not read any image in {img_dir}")
        return

    print(f"\nimage sizes (sampled {len(img_files)}): {sizes.most_common(3)}")

    (img_w, img_h), _ = sizes.most_common(1)[0]

    def pct(values: list[float], p: float) -> float:
        s = sorted(values)
        return s[int(p * (len(s) - 1))]

    print(f"\nbox size in pixels at {img_w}x{img_h} (this is the feasibility number):")
    for p, tag in [(0.05, " 5th"), (0.50, "50th"), (0.95, "95th")]:
        print(f" {tag} pct: {pct(widths, p) * img_w:6.1f} x {pct(height, p) * img_h:6.1f}")

    median_px = min(pct(widths, 0.5) * img_w, pct(height, 0.5) * img_h)
    if median_px < 16:
        print(f"{'='*6} Yo these results are not chill dog, px: {median_px:.1f} / 16, hella not chill {'='*6}")
    else:
        print(f"\nOK: median box ~{median_px:.0f}px, comfortably resolvable.")


if __name__ == "__main__":
    HERE = Path(__file__).resolve().parent
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "data" / "datasets"

    for name in ("cards", "chips"):
        ds_dir = path / name
        if (ds_dir / "data.yaml").exists():
            audit(ds_dir)
        else:
            print(f"!! no data.yaml at {ds_dir / 'data.yaml'}")
