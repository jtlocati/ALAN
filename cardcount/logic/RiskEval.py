import math

PRIOR = 0.005
DECAY = 0.98
BET_DEADBAND = 10
SPREAD_MIN = 4.0
SPREAD_ROUNDS = 20
SPREAD_CAP = 40
TAKE_ROUNDS = 100

LLR_DEV_COUNT = 2.08
LLR_DEV_NORM = -1.20
LLR_STRAT_ERROR = -0.60
LLR_BET_WITH = 0.53
LLR_BET_AGAINST = -1.61
LLR_FLAT_BETTOR = -2.00
LLR_WINNING = 0.80


def StartingOdds() -> float:
    return math.log(PRIOR / (1.0 - PRIOR))


def DecayOdds(LogOdds) -> float:
    Base = StartingOdds()
    Drift = LogOdds - Base
    return Base + (Drift * DECAY)


def ScoreMove(ActualMove, PlayerCharNORM, PlayerCharCOUNT) -> float:
    if (ActualMove != "HIT" and ActualMove != "STAND"):
        return 0.0

    if (PlayerCharNORM != "HIT" and PlayerCharNORM != "STAND"):
        return 0.0

    if (PlayerCharCOUNT != "HIT" and PlayerCharCOUNT != "STAND"):
        return 0.0

    if (PlayerCharNORM == PlayerCharCOUNT):
        if (ActualMove != PlayerCharNORM):
            return LLR_STRAT_ERROR
        return 0.0

    if (ActualMove == PlayerCharCOUNT):
        return LLR_DEV_COUNT

    if (ActualMove == PlayerCharNORM):
        return LLR_DEV_NORM

    return LLR_STRAT_ERROR


def ScoreBet(PotDiff, Count) -> float:
    if (abs(PotDiff) <= BET_DEADBAND):
        return 0.0

    if (Count == 0):
        return 0.0

    if (Count > 0 and PotDiff > 0):
        return LLR_BET_WITH

    if (Count < 0 and PotDiff < 0):
        return LLR_BET_WITH

    return LLR_BET_AGAINST


def BetSpread(POT_HISTORY) -> float:
    Bets = []

    for Bet in POT_HISTORY:
        if (Bet > 0):
            Bets.append(Bet)

    if (len(Bets) < 2):
        return 1.0

    Low = min(Bets)
    High = max(Bets)

    if (Low <= 0):
        return 1.0

    return High / Low


def ScoreSpread(POT_HISTORY) -> float:
    if (len(POT_HISTORY) < SPREAD_ROUNDS):
        return 0.0

    Spread = BetSpread(POT_HISTORY)

    if (Spread < SPREAD_MIN):
        return LLR_FLAT_BETTOR

    return 0.0


def SpreadCeiling(POT_HISTORY) -> int:
    if (len(POT_HISTORY) < SPREAD_ROUNDS):
        return 100

    Spread = BetSpread(POT_HISTORY)

    if (Spread < SPREAD_MIN):
        return SPREAD_CAP

    return 100


def ScoreTake(playerTake, POT_HISTORY) -> float:
    if (len(POT_HISTORY) < TAKE_ROUNDS):
        return 0.0

    Wagered = 0

    for Bet in POT_HISTORY:
        Wagered = Wagered + Bet

    if (Wagered <= 0):
        return 0.0

    Edge = playerTake / Wagered

    if (Edge > 0.01):
        return LLR_WINNING

    return 0.0


def aggregatePlayerRisk(LogOdds, PotDiff, Count, ActualMove, PlayerCharNORM, PlayerCharCOUNT) -> float:
    Evidence = 0.0

    Evidence = Evidence + ScoreMove(ActualMove, PlayerCharNORM, PlayerCharCOUNT)
    Evidence = Evidence + ScoreBet(PotDiff, Count)

    return LogOdds + Evidence


def RiskPercent(LogOdds, playerTake, POT_HISTORY) -> int:
    Adjusted = LogOdds

    Adjusted = Adjusted + ScoreSpread(POT_HISTORY)
    Adjusted = Adjusted + ScoreTake(playerTake, POT_HISTORY)

    if (Adjusted > 30.0):
        Adjusted = 30.0

    if (Adjusted < -30.0):
        Adjusted = -30.0

    Chance = 1.0 / (1.0 + math.exp(-Adjusted))

    Percent = int(round(Chance * 100))

    Ceiling = SpreadCeiling(POT_HISTORY)

    if (Percent > Ceiling):
        return Ceiling

    return Percent


def RiskLabel(RiskScore, Rounds) -> str:
    if (Rounds < 5):
        return "SAMPLING"

    if (RiskScore >= 80):
        return "COUNTING"

    if (RiskScore >= 50):
        return "WATCH"

    if (RiskScore >= 20):
        return "ELEVATED"

    return "CLEAR"
