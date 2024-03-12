#!/usr/bin/python3

import unittest
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from action import SwapFirstPlayerAction,PassAction

def test_contestants():
    c1 = Contestant(amber_amethyst, RandomController('test1'))
    c2 = Contestant(sapphire_steel, RandomController('test2'))
    return [c1,c2]

class TestDieRoll(unittest.TestCase):
    def test_game_create(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        self.assertEqual(game.phase, GamePhase.DIE_ROLL)

    def test_swap_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        current_controller = game.get_controller()

        # env should go first
        self.assertEqual(current_controller.name, 'env')
        actions = game.get_actions()
        self.assertEqual(len(actions), 2)

        game.process_action(SwapFirstPlayerAction())

        # assert the players are swapped
        self.assertEqual(game.p1.controller.name, 'test2')
        self.assertEqual(game.p2.controller.name, 'test1')
        self.assertEqual(game.phase, GamePhase.DRAW_STARTING_HAND)

    def test_no_swap_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        current_controller = game.get_controller()

        # env should go first
        self.assertEqual(current_controller.name, 'env')
        actions = game.get_actions()
        self.assertEqual(len(actions), 2)

        game.process_action(PassAction())

        # assert the players are swapped
        self.assertEqual(game.p1.controller.name, 'test1')
        self.assertEqual(game.p2.controller.name, 'test2')
        self.assertEqual(game.phase, GamePhase.DRAW_STARTING_HAND)


if __name__ == '__main__':
    unittest.main()
