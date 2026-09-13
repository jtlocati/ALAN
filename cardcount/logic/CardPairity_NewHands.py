#def ReturnHand(delaerDetections, PlayerDetections):


def IsPlaying(dealerCards, Playercards) -> str:
    if (len(dealerCards) > 1 and len(Playercards)> 1):
        return "ROUND IN PROGRESS"
    if (len(dealerCards) == 1 or len(Playercards) == 1):
        return "CARDS BEING DELT"
    if (len(dealerCards) == 0 or len(Playercards) == 0):
        return "ROUND OVER"

    return "UNDEFINED"

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