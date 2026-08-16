from pathlib import Path
from ultralytics import YOLO

BJ_COUNTS = {
    "2": +1, "3": +1, "4": +1, "5": +1, "6": +1,
    "7": +0, "8": +0, "9": +0,
    "10": -1, "J": -1, "Q": -1, "K": -1
}


def rankCards(label: str) -> str:
    #clean labels to ignore suite
    return label[:-1]

def main(weights: str, data: str) -> None:
    model = YOLO(weights)
    mod = model.val(data=data, split="test", plots=True)
    if (not isinstance(mod.names, dict)):
        names = mod.names
    else:
        dict(enumerate(mod.names))

    #per-class evaluation
    rows = []
    for i, cls in enumerate(mod.box.ap_class_index):
        rows.append(names[int(cls)], float(mod.box.p[i]), float(mod.box.r[i]), float(mod.box.ap50[i]))

    rows.sort(key=lambda r: r[2])

    for name, prec, recal, map in rows:
        if recal < 0.85:
            flag = True
        if flag:
            print(f"{'='*6}{name} => WEAK {'='*6}")
            print(f"Precision: {prec}\n Recall: {recal} \n mAP50: {map}")



if __name__ == "__main__":
    main()