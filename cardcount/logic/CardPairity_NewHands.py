#def ReturnHand(delaerDetections, PlayerDetections):


def IsPlaying(dealerCards, Playercards) -> str:
    if (len(dealerCards) >= 1 and len(Playercards)> 1):
        return "ROUND IN PROGRESS"
    if (len(dealerCards) == 1 or len(Playercards) == 1):
        return "CARDS BEING DELT"
    if (len(dealerCards) == 0 and len(Playercards) == 0):
        return "TABLE CLEAR"
    if (len(dealerCards) == 0 or len(Playercards) == 0):
        return "ROUND OVER"


    return "UNDEFINED"

def PotExsistance(PotTotal, TableProgress) -> str:
    if PotTotal != 0 and TableProgress == "TABLE CLEAR":
        return "BETTING"
    if PotTotal != 0:
        return "GAME POT"
    if TableProgress == "CARDS BEING DELT" or TableProgress == "ROUND IN PROGRESS":
        return "FLUKE PLAY"
    return "IDLE"

def HandVaule(PlayStatus, DealerCards, PlayerCards):
    PlayerHandValue = [0,0]
    DealerHandValue = [0,0]
    DealerAces = 0
    PlayerAces = 0
    Status = "HARD"

    if (PlayStatus == "ROUND IN PROGRESS" or PlayStatus == "CARDS BEING DELT"):
        for i in DealerCards:
            try:
                DealerHandValue[0] = DealerHandValue[0] + int(i)
            except ValueError:
                if i == "A":
                    DealerAces = DealerAces + 1
                    DealerHandValue[0] = DealerHandValue[0] + 1
                else:
                    DealerHandValue[0] = DealerHandValue[0] + 10
        for i in PlayerCards:
            try:
                PlayerHandValue[0] = PlayerHandValue[0] + int(i)
            except ValueError:
                if i == "A":
                    PlayerAces = PlayerAces + 1
                    PlayerHandValue[0] = PlayerHandValue[0] + 1
                else:
                    PlayerHandValue[0] = PlayerHandValue[0] + 10

        DealerHandValue[1] = DealerHandValue[0]
        if (DealerAces > 0 and (DealerHandValue[0] + 10) <= 21):
            DealerHandValue[1] = DealerHandValue[0] + 10

        PlayerHandValue[1] = PlayerHandValue[0]
        if (PlayerAces > 0 and (PlayerHandValue[0] + 10) <= 21):
            PlayerHandValue[1] = PlayerHandValue[0] + 10
            Status = "SOFT"



    return PlayerHandValue, DealerHandValue, Status, DealerAces


#in determineing the winner we are assuming that the dealer must stand on a soft 17
def DealerMustHit(DealerValue, Dealer_ace) -> bool:
    if (DealerValue[0] > 21):
        return False

    Best = DealerValue[1]

    if (Best < 17):
        return True

    if (Best == 17 and Dealer_ace == "SOFT"):
        return True

    return False


def WhoWinner(DealerValue, PlayerValue, HandProgress, Dealer_ace) -> str:
    # Busts resolve the instant they happen, whatever the round status.
    if (PlayerValue[0] > 21):
        return "DEALER"
    if (DealerValue[0] > 21):
        return "PLAYER"

    # Table is empty or unreadable. Nothing to judge.
    if (HandProgress != "ROUND IN PROGRESS"):
        return "NON-RES"

    # Revealed, but still drawing. Comparing now would judge a half hand.
    if (DealerMustHit(DealerValue, Dealer_ace)):
        return "NON-RES"

    PlayerBest = PlayerValue[1]
    DealerBest = DealerValue[1]

    if (PlayerBest > DealerBest):
        return "PLAYER"
    if (DealerBest > PlayerBest):
        return "DEALER"

    return "PUSH"

def playerHitStatus(PlayerCards) -> int:
    stat = len(PlayerCards) - 2
    if stat < 0:
        return 0
    return stat