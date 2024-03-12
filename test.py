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

class SwapFirstController(Controller):
    def __init__(self,name):
        super().__init__(name)

    def chooseAction(self,actions):
        if any(type(x) is SwapFirstPlayerAction for x in actions):
            return SwapFirstPlayerAction()
        else:
            return actions[0]

class PassController(Controller):
    def __init__(self,name):
        super().__init__(name)

    def chooseAction(self,actions):
        if any(type(x) is PassAction for x in actions):
            return PassAction()
        else:
            return actions[0]


class TestGameInit(unittest.TestCase):
    def test_game_create(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        self.assertEqual(game.phase, GamePhase.DIE_ROLL)

    def test_swap_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],SwapFirstController('env'))
        current_controller = game.get_controller()

        # env should go first
        self.assertEqual(current_controller.name, 'env')
        actions = game.get_actions()
        chosen_action=current_controller.chooseAction(actions)

        # should be a swap first player action
        self.assertTrue(type(chosen_action) is SwapFirstPlayerAction)
        game.process_action(chosen_action)

        # assert the players are swapped
        self.assertEqual(game.p1.controller.name, 'test2')
        self.assertEqual(game.p2.controller.name, 'test1')
        self.assertEqual(game.phase, GamePhase.DRAW_STARTING_HAND)

    def test_no_swap_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],PassController('env'))
        current_controller = game.get_controller()

        # env should go first
        self.assertEqual(current_controller.name, 'env')
        actions = game.get_actions()
        chosen_action=current_controller.chooseAction(actions)

        # should be a swap first player action
        self.assertTrue(type(chosen_action) is PassAction)
        game.process_action(chosen_action)

        # assert the players are swapped
        self.assertEqual(game.p1.controller.name, 'test1')
        self.assertEqual(game.p2.controller.name, 'test2')
        self.assertEqual(game.phase, GamePhase.DRAW_STARTING_HAND)


if __name__ == '__main__':
    unittest.main()
