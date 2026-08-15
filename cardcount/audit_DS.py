#ensure DS is in working condtion

import sys
from collections import Counter
from pathlib import Path
import yaml


def audit(dataset: Path, sample_img: int = 300) -> None:
    config = yaml.safe_load((dataset/ "data.yaml"))
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
    print(f"{'='*6} Train Label Files: {len(labels)}")

    for lf in labels:
        for line in lf.read_text().splitline:
            parts = line.split()
            if len(parts) < 5:
                continue

            contrls = int(parts[0])
            w,h = float(parts[3]), float(parts[4])
            counts[names[contrls]] +=1
            widths.append(w)
            height.append(h)

    total = sum(counts.values())
    print(f"total boxes: {total}   mean per image: {total / max(1, len(labels)):.1f}")

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

    


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/datasets")
    for name in ("cards", "chips"):
        dir = path / name
        if (dir / "data.yaml").exists():
            audit(dir)    
