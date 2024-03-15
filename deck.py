from collections import defaultdict

class Deck:
    def __init__(self, cards):
        self.randomized_cards=defaultdict(int)
        self.total_cards=len(cards)
        for c in cards:
            self.randomized_cards[c] += 1

    def get_total_cards(self):
        return self.total_cards

    def shuffle(self):
        # nothing to do for now we currently only support randomized cards
        pass

    #TODO: later support unrandomized cards in the deck
    # effectively this function just shuffles it in for now
    def put_card_on_bottom(self,card):
        self.total_cards += 1
        self.randomized_cards[card] += 1
    
    #TODO: support draw card top and bottom
    def draw_card(self,card):
        if card in self.randomized_cards:
            self.total_cards -= 1
            self.randomized_cards[card] -= 1
            if self.randomized_cards[card] == 0:
                del self.randomized_cards[card]
    
    def get_card_choices(self):
        result=dict()
        for card,quantity in self.randomized_cards.items():
            result[card] = quantity
        return result



