
from dataclasses import dataclass, field
from controller import Controller
import random

@dataclass
class Player:
    controller: Controller
    deck: list
    hand: list = field(default_factory=lambda: [])

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_cards(self, num):
        cards_to_draw = min(len(self.deck), num)
        for x in range(cards_to_draw):
            self.hand.append(self.deck.pop())

    def print_hand(self):
        for x in self.hand:
            print(x.name)


def create_player(contestant):
    return Player(contestant.controller, contestant.deck.cards)
