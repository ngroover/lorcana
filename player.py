
from dataclasses import dataclass, field
from controller import Controller
from action import MulliganAction
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

    def get_mulligans(self):
        return list(map(lambda x: MulliganAction(x), self.hand))

    def mulligan_card(self, card):
        print(f'mulliganed {card}')
        self.hand.remove(card)


def create_player(contestant):
    return Player(contestant.controller, contestant.deck.cards)
