#!/usr/bin/python3

import unittest
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController
from game import Game,GamePhase,PlayerTurn

def test_contestants():
    c1 = Contestant(amber_amethyst, RandomController('p1'))
    c2 = Contestant(sapphire_steel, RandomController('p2'))
    return [c1,c2]

class TestGameInit(unittest.TestCase):
    def test_game_create(self):
        c = test_contestants()
        game = Game(c[0],c[1])
        self.assertEqual(len(game.p1.hand),7)
        self.assertEqual(len(game.p2.hand),7)
        self.assertEqual(game.phase, GamePhase.MULLIGAN)
        self.assertEqual(game.player, PlayerTurn.PLAYER1)

if __name__ == '__main__':
    unittest.main()
