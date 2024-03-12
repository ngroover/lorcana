#!/usr/bin/python3

import unittest
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController
from game import Game,GamePhase,PlayerTurn
from test import test_contestants
from action import PassAction,MulliganAction

def simple_test_game():
    c = test_contestants()
    game = Game(c[0],c[1])
    # simplify it by removing 4 cards from hand so theres only 3
    for x in range(4):
        game.p1.hand.pop()
        game.p2.hand.pop()
    return game

class TestMulligan(unittest.TestCase):
    def test_p1_mulligan_choices(self):
        g = simple_test_game()

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,3)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),4)

    def test_p2_mulligan_choices(self):
        g = simple_test_game()
        g.player = PlayerTurn.PLAYER2
        g.swap_current_player()

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,3)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),4)

if __name__ == '__main__':
    unittest.main()
