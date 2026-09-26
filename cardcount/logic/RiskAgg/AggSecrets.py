#auto index of possible people counting at any given table (not used)
PRIOR = 0.005
#how much info about a risk metric persists from round-to-round
DECAY = 0.98
#Doller change that is sounted as non-suspect
SUSSY_MONEY = 20
#COUNTER needs roughly this mutch spread to be counted
SPREAD_MIN = 4.0
#rounds of spreading beofore being counted
SPREAD_WINDOW = 20
#Cealing for a player that never spreads
SPRED_CAP = 40
#Standard deviation of one blackjack round in betting units.
ROUND_SD = 1.15
#What the average person will make per round
BASIC_MAKE = -0.005
#fewest rounds before a count means somthing
TAKE_ROUNDS = 20
#Fewrst rounds needed in count buckets before being compared
SPLIT_ROUNDS = 15
#how much higher a count buckect must be freater than the norm to be concitered real
SPLIT_GAP = 0.25
#Hard limit on both profit signals put together
PROFIT_CAP = 1.5
#log(0.80 / 0.10). A correct off index deviation.
LLR_DEV_COUNT = 2.08
#log(0.15 / 0.50). Basic strategy move on a hand where the count said otherwise.
LLR_DEV_NORM = -1.20
#log(0.03 / 0.055) acceptabel misplayed hands
LLR_STRAT_ERROR = -0.60
#log(0.85 / 0.50). Bet moved the way the count pointed.
LLR_BET_WITH = 0.53
#log(0.10 / 0.50). Bet moved against the count, which no counter does.
LLR_BET_AGAINST = -1.61
#Applied once, not per round, to a player who never spreads.
LLR_FLAT_BETTOR = -2.00
#two stdios above stabdard for winning:
LLR_WINNING = 0.35
#Three sigma. Rarer and worth more.
LLR_WINNING_STRONG = 0.7
#Winning concentrated in the rich part of the shoe. Worth more than raw profit
LLR_COUNTED_WINNING = 1.10
