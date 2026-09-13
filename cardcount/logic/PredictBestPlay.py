#include logic that parses the arrays given by the model and analises by the reading class from main
from cardcount.vision_detection.ChipVision import DENOMINATIONS
from cardcount.vision_detection.CardVison import BJ_COUNTS

#find likley move that would be charictaristic of a normal player
def FindLikleyMoveNorm(RoundProgression, DealerHandValue, PlayeHandValue, HandType, D_ace) -> str:
    if RoundProgression == "ROUND IN PROGRESS":
        if HandType == "HARD":
            if (PlayeHandValue[0] <= 11 and HandType == "HARD"):
                return "HIT"

            if ((PlayeHandValue[0] == 12) and ( 4 <= DealerHandValue[0] <= 6)):
                return "HIT"

            if ((13<= PlayeHandValue[0] <=16 ) and not (2<= DealerHandValue <=6)):
                return "HIT"

            if (PlayeHandValue[0] >= 17):
                return "HIT"

            return "STAND"
        if (PlayeHandValue[1] <= 17):
            return "HIT"
        if ((PlayeHandValue[1] == 18) and (DealerHandValue[1] == 9 or DealerHandValue[1] == 10 or (D_ace)) or (3<= DealerHandValue[1] <=6 )):
            return "HIT"

        return "STAND"
    



    