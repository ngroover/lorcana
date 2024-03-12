
from dataclasses import dataclass
from player import Player
from player import create_player

import random

@dataclass
class Game:
    pl: Player
    p2: Player
    currentPlayer: Player

    def __init__(self, contestant1, contestant2):
        self.p1 = create_player(contestant1)
        self.p2 = create_player(contestant2)
        if random.randint(1,2) == 1:
            self.currentPlayer = self.p1
        else:
            self.currentPlayer = self.p2
        print(f'{self.currentPlayer.controller.name} goes first')
        self.p1.shuffle_deck()
        self.p2.shuffle_deck()
        self.p1.draw_cards(7)
        self.p2.draw_cards(7)
        print(f'p1 drew')
        self.p1.print_hand()
        print(f'p2 drew')
        self.p2.print_hand()
