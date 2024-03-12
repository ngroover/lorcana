#!/usr/bin/python3

from game import Game
from contestant import create_contestant

def print_stats(deck):
    inkables = sum(1 for x in deck.cards if x.inkable)
    total = len(deck.cards)
    print(f'total cards: {total}')
    print(f'Inkable: {inkables}/{total}')
    print(f'Non-Inkable: {total-inkables}/{total}')
    for c in range(1,9):
        cost = sum(1 for x in deck.cards if x.cost == c)
        print(f'{c} cost: {cost} ')


if __name__ == '__main__':
    print('Create player 1')
    c1 = create_contestant()
    print('Create player 2')
    c2 = create_contestant()
    game = Game(c1,c2)
    acts = game.get_actions()
    for a in acts:
        print(a)

