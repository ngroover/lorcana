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
    return game

class TestMulligan(unittest.TestCase):
    def test_p1_mulligan_choices(self):
        g = simple_test_game()

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,7)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),8)

    def test_p2_mulligan_choices(self):
        g = simple_test_game()
        g.player = PlayerTurn.PLAYER2
        g.swap_current_player()

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,7)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),8)

    def test_p1_mulligan(self):
        g = simple_test_game()

        actions = g.get_actions()
        # do the first mulligan
        g.process_action(next(filter(lambda x: type(x) is MulliganAction, actions)))
        
        self.assertEqual(len(g.p1.hand), 6)
        self.assertEqual(len(g.p1.pending_mulligan), 1)
        self.assertEqual(len(g.p2.hand), 7)
        self.assertEqual(len(g.p2.pending_mulligan), 0)

    def test_p2_mulligan(self):
        g = simple_test_game()
        g.swap_current_player()

        actions = g.get_actions()
        # do the first mulligan
        g.process_action(next(filter(lambda x: type(x) is MulliganAction, actions)))
        
        self.assertEqual(len(g.p1.hand), 7)
        self.assertEqual(len(g.p1.pending_mulligan), 0)
        self.assertEqual(len(g.p2.hand), 6)
        self.assertEqual(len(g.p2.pending_mulligan), 1)

    def test_p1_pass_mulligan(self):
        g = simple_test_game()

        actions = g.get_actions()
        # immediately pass
        g.process_action(next(filter(lambda x: type(x) is PassAction, actions)))
        
        # make sure we still have 7 cards and now its player 2 turn
        self.assertEqual(len(g.p1.hand), 7)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

    def test_p1_pass_mulligan(self):
        g = simple_test_game()
        g.swap_current_player()

        actions = g.get_actions()
        # immediately pass
        g.process_action(next(filter(lambda x: type(x) is PassAction, actions)))
        
        # make sure we still have 7 cards and now its player 2 turn
        self.assertEqual(len(g.p1.hand), 7)
        # TEMPORARILY This is the GAME_OVER phase
        self.assertEqual(g.phase, GamePhase.GAME_OVER)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

    def test_p1_full_mulligan(self):
        g = simple_test_game()

        actions = g.get_actions()
        # take all mulligan actions
        for a in filter(lambda x: type(x) is MulliganAction, actions):
            g.process_action(a)

        self.assertEqual(len(g.p1.hand), 0)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

        g.process_action(next(filter(lambda x: type(x) is PassAction, actions)))
        
        # make sure we still have 7 cards and now its player 2 turn
        self.assertEqual(len(g.p1.hand), 7)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

    def test_p2_full_mulligan(self):
        g = simple_test_game()
        g.swap_current_player()

        actions = g.get_actions()
        # take all mulligan actions
        for a in filter(lambda x: type(x) is MulliganAction, actions):
            g.process_action(a)

        self.assertEqual(len(g.p2.hand), 0)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

        g.process_action(next(filter(lambda x: type(x) is PassAction, actions)))
        
        # make sure we still have 7 cards and now its player 2 turn
        self.assertEqual(len(g.p1.hand), 7)
        self.assertEqual(g.phase, GamePhase.GAME_OVER)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

if __name__ == '__main__':
    unittest.main()
