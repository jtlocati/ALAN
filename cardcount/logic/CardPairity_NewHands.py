#def ReturnHand(delaerDetections, PlayerDetections):


def IsPlaying(dealerCards, Playercards) -> str:
    if (len(dealerCards) > 1 and len(Playercards)> 1):
        return "HAND IN PROGRESS"
    if (len(dealerCards) == 1 or len(Playercards) == 1):
        return "CARDS BEING DELT"
    if (len(dealerCards) == 0 or len(Playercards) == 0):
        return "ROUND OVER"

    return "UNDEFINED"

def HandVaule(DealerCards, PlayerCards):
    PlayerHandValue = [0,0]
    DealerHandValue = [0,0]
    while (IsPlaying(DealerCards, PlayerCards)):
        for i in DealerCards:
            try:
                DealerCards[0] = DealerHandValue[0] + int(i)
            except ValueError:
                if i == "A":
                    if (DealerHandValue + 11 ) > 21:
                        DealerHandValue[0] = DealerHandValue[0] + 1
                    else:
                        DealerHandValue[0] = DealerHandValue[0] + 1
                        DealerHandValue[1] = DealerHandValue[1] + 11
                else:
                    DealerHandValue[0] = DealerHandValue[0] + 10
        for i in PlayerCards:
            try:
                PlayerCards[0] = PlayerHandValue[0] + int(i)
            except ValueError:
                if i == "A":
                    if (PlayerHandValue + 11 ) > 21:
                        PlayerHandValue[0] = PlayerHandValue[0] + 1
                    else:
                        PlayerHandValue[0] = PlayerHandValue[0] + 1
                        PlayerHandValue[1] = PlayerHandValue[1] + 11
                else:
                    PlayerHandValue[0] = PlayerHandValue[0] + 10
    return PlayerHandValue, DealerHandValue



