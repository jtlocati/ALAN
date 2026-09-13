#include logic that parses the arrays given by the model and analises by the reading class from main
from cardcount.vision_detection.ChipVision import DENOMINATIONS
from cardcount.vision_detection.CardVison import BJ_COUNTS

#find likley move that would be charictaristic of a normal player
def FindLikleyMoveNorm(DealerCards, PlayeCards) -> :
    DealerHandValue = 0
    PlayerHandValue = 0
    Assumed = False

    if len(DealerCards) == 1:
        DealersCard = DealerCards.get(DealerCards[0])
        DealersCard  = BJ_COUNTS.get(DealersCard)
        DealerHandValue = DealersCard + 10
        Assumed = True

    else:
        for i in DealerCards:
            DealerHandValue += BJ_COUNTS(i, 0)

    for i in PlayeCards:
        PlayerHandValue += BJ_COUNTS.get(i, 0)

    PlayerDealerDiff = PlayerHandValue - DealerHandValue

    



    