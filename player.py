
from dataclasses import dataclass
from controller import Controller
import random

@dataclass
class Player:
    controller: Controller
    deck: list

    def shuffle_deck(self):
        random.shuffle(self.deck)


def create_player(contestant):
    return Player(contestant.controller, contestant.deck.cards)
