#ensure DS is in working condtion

import sys
from collections import Counter
from pathlib import Path
import yaml
from PIL import Image


def audit(dataset: Path, sample_img: int = 300) -> None:
    config = yaml.safe_load((dataset / "data.yaml").read_text(encoding="utf-8"))
    #check class names
    names = config["names"]
    if isinstance(names, dict):
        for i in sorted(names):
            names = names[i]
            print(f"{'='*6}{dataset.name}{'='*6}")
            print(f"classes: {len(names)}: {names}")

    counts: Counter[str] = Counter()
    #bouding boxes
    widths: list[float] = []
    height: list[float] = []

    labels = dataset / "train" / "labels"
    files_labels = sorted(labels.glob("*.txt"))
    print(f"{'='*6} Train Label Files: {len(files_labels)}")

    for lf in labels:
        for line in files_labels.read_text().splitline:
            parts = line.split()
            if len(parts) < 5:
                continue

            contrls = int(parts[0])
            w,h = float(parts[3]), float(parts[4])
            counts[names[contrls]] +=1
            widths.append(w)
            height.append(h)

    total = sum(counts.values())
    print(f"total boxes: {total}   mean per image: {total / max(1, len(files_labels)):.1f}")

    print("rarest 8")
    for name, n, in counts.most_common[-8]:
        print(f"{name} : {n:>5}")
    print("common 8")
    for name, n in counts.most_common[8]:
        print(f"{name} => {n:>5}")


    missing_labels = []
    for n in names:
        if counts[n] == 0:
            missing_labels.append(counts[n])

    print(f"missing classes: {missing_labels}")

    ratio = max(counts.values()) / max(1, min(counts.values()))

    print(f"imbalance ratio: {ratio}")

    #find box resolution + resolvable size BB scope 
    img_dir = dataset / "train" / "images"
    img_files = sorted(img_dir.iterdir())[:sample_img]
    sizes = Counter(Image.open(p).size for p in img_files)
    print(f"\nimage sizes (sampled {len(img_files)}): {sizes.most_common(3)}")

    (img_w, img_h), _ = sizes.most_common(1)[0]

    def pct(values: list[float], p: float) -> float:
        s = sorted(values)
        return s[int(p * (len(s) - 1))]

    print(f"\nbox size in pixels at {img_w}x{img_h} (this is the feasibility number):")
    for p, tag in [(0.05, " 5th"), (0.50, "50th"), (0.95, "95th")]:
        print(f" {tag} pct: {pct(widths, p) * img_w:6.1f} x {pct(height , p) * img_h:6.1f}")

    median_px = min(pct(widths, 0.5) * img_w, pct(height, 0.5) * img_h)
    if median_px < 16:
        print(f"{'='*6} Yo these results are not chill dog, px: {median_px} / 16, hella not chill {'='*6}")

    else:
        print(f"\nOK: median box ~{median_px:.0f}px, comfortably resolvable.")




if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/datasets")
    for name in ("cards", "chips"):
        dir = path / name
        if (dir / "data.yaml").exists():
            audit(dir)    
