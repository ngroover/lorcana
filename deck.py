from collections import defaultdict

class Deck:
    def __init__(self, cards):
        self.randomized_cards=defaultdict(int)
        self.total_cards = len(cards)
        for c in cards:
            self.randomized_cards[c] += 1

    def get_card_probabilities(self):
        result=dict()
        for card,quantity in self.randomized_cards.items():
            result[card] = quantity/self.total_cards
        return result



