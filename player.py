
from dataclasses import dataclass, field
from controller import Controller
from action import MulliganAction
import random

@dataclass
class Player:
    controller: Controller
    deck: list
    hand: list = field(default_factory=lambda: [])
    pending_mulligan: list = field(default_factory=lambda: [])

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def draw_cards(self, num):
        cards_to_draw = min(len(self.deck), num)
        for x in range(cards_to_draw):
            top_card = self.deck.pop()
            print(f'Drew {top_card}')
            self.hand.append(top_card)

    def print_hand(self):
        for x in self.hand:
            print(x.name)

    def get_mulligans(self):
        return list(map(lambda x: MulliganAction(x), self.hand))

    def mulligan_card(self, card):
        print(f'mulliganed {card}')
        self.hand.remove(card)
        self.pending_mulligan.append(card)

    def finish_mulligan(self):
        self.draw_cards(len(self.pending_mulligan))
        self.deck.extend(self.pending_mulligan)
        self.shuffle_deck()


def create_player(contestant):
    return Player(contestant.controller, contestant.deck.cards)
