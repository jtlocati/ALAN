#OMG LOOK AT ALL THESE COMMENTS :)
from cardcount.logic.RiskAgg.AggSecrets import *
import math

#defines log odds of prior rounds as a float
def StartingOdds() -> float:
    return math.log(PRIOR / (1 - PRIOR))

#Takes the running log odds and pulls it one step back toward the prior.
#Called once per round rather than once per observation, so forgetting is tied
#to hands played instead of to how much evidence happened to arrive.
def DecayOdds(LogOdds) -> float:
    Base = StartingOdds()
 
    Drift = LogOdds - Base
    return Base + (Drift * DECAY)

#find when PlayerCharNORM != PlayerCharCOUNT, weight metric off these differences
def ScoreMove(PlayerMove, PlayerHits, PlayerCharNORM, playerCharCOUNT) -> float:
    #possible error handling
    if (PlayerMove != "HIT" and PlayerMove != "STAND"):
        return 0.0
    if (PlayerMove == "HIT" and PlayerHits <= 0):
        return 0.0
    #once dealer has drawn:
    if (PlayerCharNORM != "HIT" and PlayerCharNORM != "STAND"):
        return 0.0
    if (playerCharCOUNT != "HIT" and playerCharCOUNT != "STAND"):
        return 0.0

    #if both player preciction models have the same outcome -> void round as no difference or meaningfull tell can be derived
    if(PlayerCharNORM == playerCharCOUNT):
        #if player does what neither of them suggest
        if(PlayerMove != PlayerCharNORM):
            return LLR_STRAT_ERROR
        return 0.0

    #The tow player prediction models != oneanother

    if PlayerMove == playerCharCOUNT:
        return LLR_DEV_COUNT
    if PlayerMove == PlayerCharNORM:
        return LLR_DEV_NORM
    return LLR_STRAT_ERROR

#pot trend analysis
def ScorePot(PotTotal, PotDiff, Count) -> float:
    #possible error
    if (PotTotal <= 0):
        return 0.0

    #no meaningfull pot change
    if(abs(PotDiff) <= SUSSY_MONEY):
        return 0.0
    
    #no count means so strat is feasable
    if(Count == 0):
        return 0.0

    #this is where the fun begins (lowkey a starwars ref)

    #Shoe high && Bet increce == Stinky counter guy
    if (Count > 0 and PotDiff > 0):
        return LLR_BET_WITH

    #Shoe High && bet down == also Stinky cheater-man
    if (Count < 0 and PotDiff < 0):
        return LLR_BET_WITH

    #ALL Else is char of stinky normie
    return LLR_BET_AGAINST


#ratio of the biggest bet to the smallest
def BetSpread(POT_HISTORY) -> float:
    Bets = []

    for Bet in POT_HISTORY:
        if (Bet > 0):
            Bets.append(Bet)

    #one bet has no spread
    if (len(Bets) < 2):
        return 1.0

    Low = min(Bets)
    High = max(Bets)

    if (Low <= 0):
        return 1.0

    return High / Low

#a flat bettor cannot profit off a count, so this counts against them
def ScoreSpread(POT_HISTORY) -> float:
    if (len(POT_HISTORY) < SPREAD_WINDOW):
        return 0.0

    if (BetSpread(POT_HISTORY) < SPREAD_MIN):
        return LLR_FLAT_BETTOR

    return 0.0

#hard ceiling rather than another additive term
def SpreadCeiling(POT_HISTORY) -> int:
    if (len(POT_HISTORY) < SPREAD_WINDOW):
        return 100

    if (BetSpread(POT_HISTORY) < SPREAD_MIN):
        return SPRED_CAP

    return 100


#find if a players take is un-usual
def ScoreTaken(playerTake, ROUND_RESULTS) -> float:
    #clear losing players
    if playerTake <=0:
        return 0.0
    if len(ROUND_RESULTS) < TAKE_ROUNDS:
        return 0.0

    #running total of betting results in a stdio unit
    UnitsWon = 0
    Rounds  = 0

    for Record in ROUND_RESULTS:
        RoundProfit = Record[1]
        RoundBet = Record[2]

        #skip a possible unbet round
        if RoundBet <= 0:
            continue

        UnitsWon = UnitsWon + (RoundProfit / RoundBet)
        Rounds += 1

    #Rid another non-thregtening possibility
    if (Rounds < TAKE_ROUNDS):
        return 0.0

    #what a normal person would have at this point
    Expected = BASIC_MAKE * Rounds

    #Factor luck
    Spread = ROUND_SD * math.sqrt(Rounds)
    #bad luck, non-threghtening
    if Spread <=0:
        return 0.0

    Zscore = (UnitsWon - Expected)/Spread

    if (Zscore > 3.0):
        return LLR_WINNING_STRONG
    if(Zscore > 2.0):
        return LLR_WINNING
    return 0.0

#aggregate based on count and player resoince
def ScoreCountedWinning(ROUND_RESULTS) -> float:
    HighUnits = 0.0
    HighRounds = 0
    LowUnits = 0.0
    LowRounds = 0

    for Record in ROUND_RESULTS:
        CountBefore = Record[0]
        RoundProfit = Record[1]
        RoundBet = Record[2]
 
        if (RoundBet <= 0):
            continue
 
        #This rouns result as a multiple of the stake.
        Units = RoundProfit / RoundBet

        if (CountBefore > 0):
            HighUnits = HighUnits + Units
            HighRounds = HighRounds + 1
        elif (CountBefore < 0):
            LowUnits = LowUnits + Units
            LowRounds = LowRounds + 1
 

 
    #Both buckets need enough rounds. 
    if (HighRounds < SPLIT_ROUNDS):
        return 0.0
 
    if (LowRounds < SPLIT_ROUNDS):
        return 0.0
 
    #Average units won per round in each part of the shoe.
    HighRate = HighUnits / HighRounds
    LowRate = LowUnits / LowRounds
 
    Gap = HighRate - LowRate
 
    if (Gap > SPLIT_GAP):
        return LLR_COUNTED_WINNING
 
    return 0.0

#bet history. Returns a whole number from 0 to 100.
def RiskPercent(LogOdds, playerTake, ROUND_RESULTS, POT_HISTORY) -> int:
    
    Adjusted = LogOdds
 
   
    Adjusted = Adjusted + ScoreSpread(POT_HISTORY)
 
    
    ProfitEvidence = 0.0
    ProfitEvidence = ProfitEvidence + ScoreTaken(playerTake, ROUND_RESULTS)
    ProfitEvidence = ProfitEvidence + ScoreCountedWinning(ROUND_RESULTS)
 
    if (ProfitEvidence > PROFIT_CAP):
        ProfitEvidence = PROFIT_CAP
 
    Adjusted = Adjusted + ProfitEvidence
 
    if (Adjusted > 30.0):
        Adjusted = 30.0
 
    if (Adjusted < -30.0):
        Adjusted = -30.0
 
    #Standard logistic, turning log odds back into a probability.
    Chance = 1.0 / (1.0 + math.exp(-Adjusted))
 
    Percent = int(round(Chance * 100))
 
    Ceiling = SpreadCeiling(POT_HISTORY)
 
    if (Percent > Ceiling):
        return Ceiling
 
    return Percent


#word shown beside the number on the overlay
def RiskLabel(RiskScore, Rounds) -> str:
    #a clean player and an unwatched player both read zero, so say which
    if (Rounds < 5):
        return "SAMPLING"

    if (RiskScore >= 80):
        return "COUNTING"

    if (RiskScore >= 50):
        return "WATCH"

    if (RiskScore >= 20):
        return "ELEVATED"

    return "CLEAR"


def aggregatePlayerRisk(PotTotal, playerTake, Count, PlayerHits, PlayerCharNORM, PlayerCharCOUNT, LogOdds, ActualMove, PotDiff, ROUND_RESULTS, POT_HISTORY):
    #Accumulator for this one observation. 
    Evidence = 0.0
 
    #Play channel. Returns zero unless a move was actually observed this call.
    Evidence = Evidence + ScoreMove(ActualMove, PlayerHits, PlayerCharNORM, PlayerCharCOUNT)
 
    #Bet channel. Returns zero unless a bet was latched this call.
    Evidence = Evidence + ScorePot(PotTotal, PotDiff, Count)
 
    #Log odds add.
    NewOdds = LogOdds + Evidence
 
    RiskScore = RiskPercent(NewOdds, playerTake, ROUND_RESULTS, POT_HISTORY)
    RiskWord = RiskLabel(RiskScore, len(POT_HISTORY))
 
    return NewOdds, RiskScore, RiskWord