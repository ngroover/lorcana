
from dataclasses import dataclass
from controller import Controller

@dataclass
class Player:
    controller: Controller
    deck: list

def create_player(contestant):
    return Player(contestant.controller, contestant.deck)
