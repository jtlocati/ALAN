from pathlib import Path
import cv2
import time

from cardcount.detections.detectors import Detector
from cardcount.metrics.eval import BJ_COUNTS, rankCards
from cardcount.vision.camera import OpenCam, draw
from cardcount.vision.table import analizeFrames
from cardcount.vision.zones import drawBands
from cardcount.logic.ConfirmCount import StreakGate
from collections import Counter
from dataclasses import dataclass
from cardcount.logic.CardPairity_NewHands import IsPlaying, HandVaule, WhoWinner, PotExsistance, playerHitStatus
from cardcount.logic.PredictBestPlay import FindLikleyMoveNorm, FindLikleyMoveNormSIMPLE, FindLikleyMoveCountSIMPLE
from cardcount.logic.CountTheCards import HandCount
from cardcount.logic.RiskAgg.RiskEval import StartingOdds, DecayOdds, aggregatePlayerRisk

CHIP_WEIGHT = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\chips_best.pt"
CARD_WEIGHT = r"C:\Users\jetlo\OneDrive\Documents\GitHub\ALAN\models\cards_best.pt"

CAM = 1
IMGSZ = 640
DEVICE = "cpu"
CARD_CONF = 0.68
CHIP_CONF = 0.30
CONF_FRAMES = 15



@dataclass(frozen=True, slots=True)
class TableReading:
    PlayerCards: list[str]
    DealerCards: list[str]
    potTotal: int
    chipColors: list[str]


def NormaliseChip(raw: str) -> str:
    return raw.strip().lower().replace(" chip", "")


DENOMINATIONS = {"white": 1, "red": 5, "blue": 10, "green": 25, "black": 100}

def readTable(view, gate) -> TableReading:
    observed = Counter()
    #find cards per person + the count it holds
    for detection in view.dealer:
        dealerKey = ("dealer", detection.label)
        #Recall the given card @ location [key] include an additional +1 trakcer per carrd instance
        observed[dealerKey] = observed[dealerKey] + 1

    for detection in view.player:
        playerKey = ("player", detection.label)
        observed[playerKey] = observed[playerKey] +1

    confirmedCards = gate.update(observed)

    dealer_cards = []
    player_cards = []

    for roleLabel, cardCount in confirmedCards.items():
        role = roleLabel[0]
        card = roleLabel[1]

        for _ in range(cardCount):
            if role == "dealer":
                dealer_cards.append(card)
            else:
                player_cards.append(card)

    dealer_cards.sort()
    player_cards.sort()

    #find count
    """runnning_count = 0

    for card in dealer_cards:
        dealerRank = rankCards(card)
        runnning_count = runnning_count + BJ_COUNTS.get(dealerRank, 0)

    for label in dealer_cards:
        playerRank = rankCards(card)
        runnning_count = runnning_count + BJ_COUNTS(playerRank, 0)"""


    #find pot
    potTotal = 0
    chipColors = []


    for detection in view.pot:
        color = NormaliseChip(detection.label)
        chipColors.append(color)

        potTotal = potTotal + DENOMINATIONS.get(color,0)

    return TableReading(
        DealerCards=dealer_cards,
        PlayerCards=player_cards,
        potTotal=potTotal,
        chipColors=chipColors
    )


def main():
    COUNT = 0
    RemoveCards = False
    CLEAR_FRAMES= 10
    PLAYER_PROFIT=0
    EmptyFrames = 0
    POT_HISTORY = []
    PotDiff = 0
    #max pot in a round
    PotWhileClear=0
    #bet latch guard
    BetLatched=False
    #running evidence total for this player
    LOG_ODDS = StartingOdds()
    RiskScore = 0
    RiskWord = "SAMPLING"
    #state carried between frames so a new card reads as a decision
    PrevHits = 0
    PrevNORM = "NONE"
    PrevCOUNT = "NONE"
    #one row per resolved round: count held at bet time, profit, stake
    ROUND_RESULTS = []

    cardModel = Detector(CARD_WEIGHT, IMGSZ, DEVICE)
    chipModel = Detector(CHIP_WEIGHT, IMGSZ, DEVICE)
    print(f"cards: {len(cardModel.names)} classes | chips: {len(chipModel.names)} classes")
    if len(cardModel.names) != 52:
        raise ValueError(f"expected 52 card classes, got {len(cardModel.names)}")

    cam = OpenCam(source=CAM)
    cardModel.warmup(cam.height, cam.width)
    chipModel.warmup(cam.height, cam.width)

    showBands = True
    gate = StreakGate(CONF_FRAMES)

    try:
        while True:
            frame = cam.read()
            if frame is None:
                continue

            view = analizeFrames(frame, cardModel, chipModel, CARD_CONF, CHIP_CONF)

            reading = readTable(view, gate)

            handProgress = IsPlaying(reading.DealerCards, reading.PlayerCards)

            PlayerHandValue, DealerHandValue, HandType, Dealer_ace = HandVaule(handProgress, reading.DealerCards, reading.PlayerCards)

            GameProgression = WhoWinner(DealerHandValue, PlayerHandValue, handProgress, Dealer_ace, reading.DealerCards)

            LikleyMove_NORM = FindLikleyMoveNormSIMPLE(reading.DealerCards,handProgress, DealerHandValue[1], PlayerHandValue, HandType, Dealer_ace)

            LikleyMove_COUNT = FindLikleyMoveCountSIMPLE(reading.DealerCards ,COUNT, HandType, DealerHandValue[1], PlayerHandValue[1])

            PotStatus = PotExsistance(reading.potTotal, handProgress)

            PlayerHitStat = playerHitStatus(reading.PlayerCards)

            #Put most rencent hand value into the count card function.
            TableEmpty = (len(reading.PlayerCards) == 0 and len(reading.DealerCards) == 0)
            #open betting window
            if TableEmpty:
                EmptyFrames = EmptyFrames + 1
            else:
                EmptyFrames = 0

            if TableEmpty:
                if EmptyFrames == CLEAR_FRAMES:
                    #Ensure that this function is used only once per round, giving the dealer to pay out the current round
                    PotWhileClear = 0
                    BetLatched = False
                    PrevHits = 0
                    PrevNORM = "NONE"
                    PrevCOUNT = "NONE"
                #ensure that the max value is always read
                if (BetLatched == False and reading.potTotal > PotWhileClear):
                    PotWhileClear = reading.potTotal
            #if table has reached a consesus on the table
            #First round == 0, nothing to compare to
            elif(BetLatched == False):
                if len(POT_HISTORY) == 0:
                    PotDiff = 0
                else:
                    #find true pot diff
                    PotDiff = PotWhileClear  - POT_HISTORY[-1]

                POT_HISTORY.append(PotWhileClear)

                LOG_ODDS = DecayOdds(LOG_ODDS)
                LOG_ODDS, RiskScore, RiskWord = aggregatePlayerRisk(PotWhileClear, PLAYER_PROFIT, COUNT, PlayerHitStat, "NONE", "NONE", LOG_ODDS, "NONE", PotDiff, ROUND_RESULTS, POT_HISTORY)

                #Close branch for next process
                BetLatched  = True


            if EmptyFrames > CLEAR_FRAMES:
                RemoveCards = False

            if handProgress == "ROUND IN PROGRESS":
                if (PlayerHitStat > PrevHits and PrevNORM != "NONE"):
                    LOG_ODDS, RiskScore, RiskWord = aggregatePlayerRisk(reading.potTotal, PLAYER_PROFIT, COUNT, PlayerHitStat, PrevNORM, PrevCOUNT, LOG_ODDS, "HIT", 0, ROUND_RESULTS, POT_HISTORY)

                PrevHits = PlayerHitStat

                if (LikleyMove_NORM == "HIT" or LikleyMove_NORM == "STAND"):
                    PrevNORM = LikleyMove_NORM
                    PrevCOUNT = LikleyMove_COUNT

            if (RemoveCards == False and GameProgression != "NON-RES" and handProgress == "ROUND IN PROGRESS"):
                if (PlayerHandValue[0] <= 21 and PrevNORM != "NONE"):
                    LOG_ODDS, RiskScore, RiskWord = aggregatePlayerRisk(reading.potTotal, PLAYER_PROFIT, COUNT, PlayerHitStat, PrevNORM, PrevCOUNT, LOG_ODDS, "STAND", 0, ROUND_RESULTS, POT_HISTORY)

                CountBefore = COUNT
                Count = HandCount(reading.PlayerCards, reading.DealerCards)
                COUNT = COUNT + Count
                RemoveCards = True

                if len(POT_HISTORY) > 0:
                    RoundBet = POT_HISTORY[-1]
                else:
                    RoundBet = 0

                RoundProfit = 0

                if GameProgression == "PLAYER":
                    RoundProfit = RoundBet
                elif GameProgression == "DEALER":
                    RoundProfit = 0 - RoundBet

                PLAYER_PROFIT = PLAYER_PROFIT + RoundProfit

                ROUND_RESULTS.append((CountBefore, RoundProfit, RoundBet))





            if view.unassigned:
                print(f"  !! cards in the betting band: {[d.label for d in view.unassigned]}")

            print(f"D {reading.DealerCards} | P {reading.PlayerCards} | pot >= ${reading.potTotal}")

            if showBands:
                drawBands(frame)

            draw(frame, view.dealer, colour=(0, 225, 0))
            draw(frame, view.player, colour=(0, 225, 0))
            draw(frame, view.pot, colour=(255, 200, 0))
            draw(frame, view.unassigned, colour=(0, 140, 255))

            cv2.putText(frame, f"pot >= ${reading.potTotal}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(frame, f"DEALER HAND {reading.DealerCards} | PLAYER HAND {reading.PlayerCards}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(frame, f"TableStatus = {handProgress} | PLR HND NORM: {HandType}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0), 2)
            cv2.putText(frame, f"Player Hand Value: {PlayerHandValue} | Dealer Hand Value: {DealerHandValue}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX,  0.8, (0, 0, 0), 2)
            cv2.putText(frame, f"Winner: {GameProgression}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX,  0.8, (0, 0, 0), 2)
            cv2.putText(frame, f"Count: {COUNT}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX,  0.8, (0, 0, 225), 2)
            cv2.putText(frame, f"Pot Diff: {PotDiff}", (10,210), cv2.FONT_HERSHEY_SIMPLEX,  0.8, (0, 0, 225), 2)
            cv2.putText(frame, f"Player has hit {PlayerHitStat} times this round", (10,240), cv2.FONT_HERSHEY_SIMPLEX,  0.8, (0, 0, 225), 2)
            cv2.putText(frame, f"PLR SHOULD NORM: {LikleyMove_NORM} | PLR HND COUNT: {LikleyMove_COUNT}", (10, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(frame, f"player take: {PLAYER_PROFIT}", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            cv2.putText(frame, f"COUNTER RISK: {RiskScore}% {RiskWord}", (10, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 225), 2)
            cv2.putText(frame, f"rounds {len(POT_HISTORY)} | results {len(ROUND_RESULTS)} | odds {LOG_ODDS:.1f}", (10, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)


            cv2.imshow("ALAN - table", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("z"):
                showBands = not showBands
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
