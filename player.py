
from dataclasses import dataclass, field
from controller import Controller
from action import MulliganAction,InkAction
from deck import Deck
from collections import Counter
import random

@dataclass
class Player:
    controller: Controller
    deck: Deck
    hand: list = field(default_factory=lambda: [])
    pending_mulligan: list = field(default_factory=lambda: [])
    inkwell: int = 0

    def get_top_card_choices(self):
        return self.deck.get_card_choices()

    def draw_card(self,card):
        self.deck.draw_card(card)
        self.hand.append(card)
    
    def print_hand(self):
        for x in self.hand:
            print(x.name)

    def get_mulligans(self):
        card_counts = set(self.hand)
        return list(map(lambda x: MulliganAction(x), card_counts))

    def mulligan_card(self, card):
        print(f'mulliganed {card}')
        self.hand.remove(card)
        self.pending_mulligan.append(card)

    def finish_mulligan(self):
        for x in self.pending_mulligan:
            self.deck.put_card_on_bottom(x)
        self.deck.shuffle()

    def get_ink_actions(self):
        inkable_cards = set(filter(lambda x: x.inkable, self.hand))
        return list(map(lambda y: InkAction(y), inkable_cards))



def create_player(contestant):
    return Player(contestant.controller, Deck(contestant.deck.cards))
