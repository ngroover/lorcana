#!/usr/bin/python3

import unittest
from contestant import Contestant
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from action import FirstPlayerAction,PassAction,DrawAction,MulliganAction
from decklists import captain_hook,aurora, maleficent,olaf,pascal,wardrobe,fire_the_cannons,dinglehopper
from test_support import test_contestants

def game_with_starting_hands(swapped):
    c = test_contestants()
    game = Game(c[0],c[1],RandomController('env'))

    game.process_action(FirstPlayerAction(swapped))
    p2cards=[captain_hook,captain_hook,captain_hook, aurora, maleficent, maleficent,maleficent]
    p1cards=[olaf,olaf,olaf,pascal,pascal,wardrobe, wardrobe]
    if swapped:
        all_cards=p2cards+p1cards
    else:
        all_cards=p1cards+p2cards
    for x in all_cards:
        game.process_action(DrawAction(x))

    return game

def game_first_turn(swapped):
    game = game_with_starting_hands(swapped)

    game.process_action(PassAction())
    game.process_action(PassAction())
    return game


class TestController(unittest.TestCase):
    def test_die_roll_controller(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        self.assertEqual(game.phase, GamePhase.DIE_ROLL)
        self.assertEqual(game.currentController.name, 'env')

    def test_swap_first_player_controller(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))

        game.process_action(FirstPlayerAction(True))
        current_controller = game.get_controller()

        self.assertEqual(game.currentController.name, 'env')
        self.assertEqual(game.currentPlayer.controller.name, 'test2')

    def test_no_swap_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))

        game.process_action(FirstPlayerAction(False))
        current_controller = game.get_controller()

        self.assertEqual(game.currentController.name, 'env')
        self.assertEqual(game.currentPlayer.controller.name, 'test1')

    def test_swap_pass_mulligan(self):
        game=game_with_starting_hands(True)

        self.assertEqual(game.currentController.name, 'test2')
        game.process_action(PassAction())
        self.assertEqual(game.currentController.name, 'test1')
        game.process_action(PassAction())

        # no drawing up
        self.assertEqual(game.currentController.name, 'test2')

    def test_no_swap_pass_mulligan(self):
        game=game_with_starting_hands(False)

        self.assertEqual(game.currentController.name, 'test1')
        game.process_action(PassAction())
        self.assertEqual(game.currentController.name, 'test2')
        game.process_action(PassAction())

        # no drawing up
        self.assertEqual(game.currentController.name, 'test1')

    def test_swap_p1_mulligan(self):
        game=game_with_starting_hands(True)

        self.assertEqual(game.currentController.name, 'test2')
        self.assertEqual(game.currentPlayer.controller.name, 'test2')
        game.process_action(MulliganAction(captain_hook))
        self.assertEqual(game.currentController.name, 'test2')
        game.process_action(PassAction())
        self.assertEqual(game.currentController.name, 'test1')
        game.process_action(PassAction())

        # p1 (test2) has to draw up
        self.assertEqual(game.currentController.name, 'env')
        self.assertEqual(PlayerTurn.PLAYER1, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test2')

        game.process_action(DrawAction(fire_the_cannons))

        self.assertEqual(game.currentController.name, 'test2')
        self.assertEqual(PlayerTurn.PLAYER1, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test2')

    def test_swap_p2_mulligan(self):
        game=game_with_starting_hands(True)

        self.assertEqual(game.currentController.name, 'test2')
        game.process_action(PassAction())

        game.process_action(MulliganAction(olaf))
        self.assertEqual(game.currentController.name, 'test1')
        game.process_action(PassAction())

        # p2 (test1) has to draw up
        self.assertEqual(game.currentController.name, 'env')
        self.assertEqual(PlayerTurn.PLAYER2, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test1')

        game.process_action(DrawAction(dinglehopper))

        self.assertEqual(game.currentController.name, 'test2')
        self.assertEqual(PlayerTurn.PLAYER1, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test2')

    def test_swap_both_mulligan(self):
        game=game_with_starting_hands(True)

        self.assertEqual(game.currentController.name, 'test2')
        game.process_action(MulliganAction(captain_hook))
        game.process_action(PassAction())

        game.process_action(MulliganAction(olaf))
        self.assertEqual(game.currentController.name, 'test1')
        game.process_action(PassAction())

        # both have to draw up
        self.assertEqual(game.currentController.name, 'env')
        self.assertEqual(PlayerTurn.PLAYER1, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test2')

        game.process_action(DrawAction(fire_the_cannons))

        self.assertEqual(game.currentController.name, 'env')
        self.assertEqual(PlayerTurn.PLAYER2, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test1')

        game.process_action(DrawAction(dinglehopper))

        self.assertEqual(game.currentController.name, 'test2')
        self.assertEqual(PlayerTurn.PLAYER1, game.player)
        self.assertEqual(game.currentPlayer.controller.name, 'test2')

    def test_pass_first_turn(self):
        game = game_first_turn(False)

        self.assertEqual(GamePhase.MAIN, game.phase)
        self.assertEqual('test1', game.currentPlayer.controller.name)
        self.assertEqual('test1', game.currentController.name)

        game.process_action(PassAction())

        self.assertEqual(GamePhase.DRAW_PHASE, game.phase)
        self.assertEqual('test2', game.currentPlayer.controller.name)
        self.assertEqual('env', game.currentController.name)

        game.process_action(DrawAction(fire_the_cannons))

        self.assertEqual(GamePhase.MAIN, game.phase)
        self.assertEqual('test2', game.currentPlayer.controller.name)
        self.assertEqual('test2', game.currentController.name)



if __name__ == '__main__':
    unittest.main()
