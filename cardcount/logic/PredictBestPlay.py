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

            if ((13<= PlayeHandValue[0] <=16 ) and not (2<= DealerHandValue[1] <=6)):
                return "HIT"

            if (PlayeHandValue[0] >= 17):
                return "HIT"

            return "STAND"
        if (PlayeHandValue[1] <= 17):
            return "HIT"
        if ((PlayeHandValue[1] == 18) and (DealerHandValue[1] == 9 or DealerHandValue[1] == 10 or (D_ace)) or (3<= DealerHandValue[1] <=6 )):
            return "HIT"

        return "STAND"


def FindLikleyMoveNormSIMPLE(DealerCards, RoundProgression, DealerHandValue, PlayeHandValue, HandType, D_ace) -> str:
    if len(DealerCards)>1:
        return "PLAYER HAS STOOD"
    if DealerHandValue == 0:
        return "NONE"
    if HandType == "SOFT":
        #soft 17 or > 17 are HIT, cannot loose from them, all SOFT > 17 should be stelt on
        if PlayeHandValue[1] <= 17:
            return "HIT"
        else:
            return "STAND"
    else:
        # >=11 cannot bust, must hit.
        if PlayeHandValue[0] <= 11:
            return "HIT"
        elif PlayeHandValue[0] >= 17:
            return "STAND"

        # 12 is dependent on dealer hand value

        elif PlayeHandValue[0] == 12:
            if  4 <= DealerHandValue <= 6:
                return "STAND"
            else:
                return "HIT"

        else:
            if DealerHandValue >= 7:
                return "HIT"
            else: 
                return "STAND" \
                ""
def FindLikleyMoveCountSIMPLE(count, stiffness, dealerValue, PlayerValue):
    if dealerValue == 0:
        return "NONE"
    if stiffness == "HARD":
        if PlayerValue == 16 and dealerValue == 10:
            if count >= 0:
                return "STAND"
            else:
                return "HIT"

        if PlayerValue == 15 and dealerValue == 10:
            if count >= 4:
                return "STAND"
            else:
                return "HIT"

        if PlayerValue == 12 and dealerValue == 3:
            if count >=2:
                return "STAND"
            else:
                return "HIT"

        if PlayerValue == 12 and dealerValue == 2:
            if count >=3:
                return "STAND"
            else:
                return "HIT"

        if PlayerValue == 12 and dealerValue == 4:
            if count < 0:
                return "HIT"
            else:
                return "STAND"

        if PlayerValue == 12 and dealerValue == 5:
            if count < -2:
                return "HIT"
            else: 
                return "STAND"

        if PlayerValue == 12 and dealerValue ==6:
            if count < -1:
                return "HIT"
            else:
                return "STAND"

        if PlayerValue == 13 and dealerValue == 2:
            if count < -1:
                return "HIT"
            else:
                return "STAND"

    if stiffness == "SOFT":
        if PlayerValue <= 17:
            return "HIT" 
        else:
            return "STAND"
    else:
        if PlayerValue <= 11:
            return "HIT"
        elif PlayerValue >= 17:
            return "STAND"
        else:
            if dealerValue >=7:
                return "HIT"
            else:
                return "STAND"

        
            



    