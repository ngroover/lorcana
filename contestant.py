
from dataclasses import dataclass
from decklists import Decklist
from decklists import decklists
from controller import Controller
from controller import create_controller


@dataclass
class Contestant:
    deck: Decklist
    controller: Controller

def create_contestant():
    controller = create_controller()
    deck = choose_deck()
    c = Contestant(deck,controller)
    return c

def choose_deck():
    while True:
        for i,d in enumerate(decklists):
            print(f'[{i+1}]. {d.name}')
        choice = int(input("Choice: "))-1
        if choice >= 0 and choice < len(decklists):
            break
    return decklists[choice]
