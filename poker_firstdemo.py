#this is a piece of code were i have used tuples,sort,list,split
from typing import Tuple,List

POKER_RANK = {
      
      '2':2, '3':3,'4':4,'5':5,'6':6,'7':7,'8':8,
      '9':9,'10':10,'11':11,'12':12,'13':13,'14':14
      
      }
def poker_hands(card: str) -> Tuple[int, str]:
    
                                          
  
    card = card.strip().upper()
    high = card[-1]
    without_high = card[:-1]
    return(POKER_RANK[without_high],high)
def poker_cards(hand_std: str) -> List[Tuple[int, str]]:
    cards = hand_std.split()
    return[poker_hands(card) for card in cards]

hands = "1010 1111"
print(poker_cards(hands))
    