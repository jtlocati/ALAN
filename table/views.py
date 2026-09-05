import json

import cv2
import numpy
from pathlib import Path
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cardcount.detections.detectors import Detector
from cardcount.logic.ConfirmCount import StreakGate
from cardcount.metrics.eval import BJ_COUNTS, rankCar
from cardcount.vision_detection.ChipVision import CHIP_NAMES, DENOMINATIONS
from cardcount.vision.table import analizeFrames
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
CARD_WEIGHTS = BASE_DIR / "models" / "cards_best.pt"
CHIP_WEIGHTS = BASE_DIR / "models" / "cards_best.pt"

IMGSZ = 640
DEVICE = "cpu"
CARD_CONF = 0.25
CHIP_CONF = 0.5

#consecutive framse needed for a hand to be current
CONF_FRAMES = 6


#initalze models as program starts up
CARD_MODEL = Detector(CARD_WEIGHTS)
CHIP_MODEL = Detector(CHIP_WEIGHTS)

CONFIRM_HAND = StreakGate(CONF_FRAMES)


def NormaliseChip(label):
    cleaned = label.strip().lower()
    cleaned = cleaned.replace(" chip", "")
    return cleaned

def index(request):
    return render(request, "table/index.html")


#render and return the page analysis pror to display to prevent redudnet analysis at runtime
def analize(request):
    raw = request.body
    if len(raw) == 0:
        return JsonResponse({"error": "empty body"}, status=400)

    byteBuff = numpy.frombuffer(raw, dtype=numpy.uint8)
    frame = cv2.imdecode(byteBuff, cv2.IMREAD_COLOR)
    if frame is None:
        return JsonResponse({"error": "could not decode the frame"}, status=400)

    view = analizeFrames(frame, CARD_MODEL, CHIP_MODEL, CARD_CONF, CHIP_CONF)

    #validate cards
    observed = {}

    for detection in view.dealer:
        key = ("dealer", detection.label)
        observed[key] = observed.get(key, 0) + 1
    for detection in view.player:
        key = ("player", detection.label)
        observed[key] = observed.get(key, 0) + 1

    confirmed_cards = CONFIRM_HAND.update(Counter(observed))

    #split cards from the total list to the player and dealer hands 
    dealer_cards = []
    player_cards = []

    for role, count in confirmed_cards.items():
        rolee = role[0]
        label = role[1]
        for _ in range (count):
            if rolee == "dealer":
                dealer_cards.append(label)
            else:
                player_cards.append(label)

    dealer_cards.sort()
    player_cards.sort()

    #count total card count
    running_count = 0
    for label in dealer_cards:
        running_count += BJ_COUNTS.get(rankCar(label), 0)

    for label in player_cards:
        running_count += BJ_COUNTS.get(rankCar(label), 0)

    #find total in pot
    pot = 0
    chip_colors = []
    for detection in view.pot:
        color = NormaliseChip(detection.label)
        chip_colors.append(color)
        pot += DENOMINATIONS.get(color)

    #initalize boxes for display
    boxes = []
    for role, detections in (("dealer", view.dealer), ("player", view.player), ("pot", view.pot), ("unassigned", view.unassigned)):
        for detection in detections:
            boxes.append({
                "role": role,
                "label": detection.label,
                "conf": round(detection.confidence, 3),
                "box": [round(value, 1) for value in detection.box],
            })

    BoxPayload = {
        "width": int(frame.shape[1]),
        "height": int(frame.shape[0]),
        "dealer": dealer_cards,
        "player": player_cards,
        "hilo": running_count,
        "pot": pot,
        "chips": color,
        "boxes": boxes,
    }

    return JsonResponse(BoxPayload)

