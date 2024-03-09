
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
