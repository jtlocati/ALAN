#Takes an infence of all cards on the table in order to return

def HandCount(CardPlayer, CardDealer):
    COUNT = 0
    CARDS = CardPlayer + CardDealer

    #Calculate players weight first
    for i in CARDS:
        try:
            Value = int(i)

            if (2 <= Value <= 6):
                COUNT+=1
            #eXPRESS STEP FOR READABILITY
            elif (6 <= Value >= 7):
                COUNT += 0
            else:
                COUNT -= 1
        except ValueError:
            COUNT -= 1

    return COUNT