#!/usr/bin/python3

import unittest
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from decklists import olaf,pascal,moana,mickey_mouse,wardrobe,dinglehopper,stitch,friends_on_the_other_side
from decklists import captain_hook,maleficent,simba,scar,one_jump_ahead,kristoff,flounder,fire_the_cannons
from controller import RandomController
from game import Game,GamePhase,PlayerTurn
from action import PassAction,MulliganAction,DrawAction
from test_support import simple_test_game

def mulligan_state_with_different_cards_game(player):
    g = simple_test_game()
    g.phase = GamePhase.MULLIGAN
    g.player = player
    if player == PlayerTurn.PLAYER1:
        g.currentPlayer = g.p1
    else:
        g.currentPlayer = g.p2

    g.p1.hand = [olaf,pascal,moana,mickey_mouse,wardrobe,dinglehopper,stitch]
    g.p2.hand = [captain_hook,maleficent,simba,scar,one_jump_ahead,kristoff,flounder]
    return g

def mulligan_state_with_duplicate_cards_game(player):
    g = simple_test_game()
    g.phase = GamePhase.MULLIGAN
    g.player = player
    if player == PlayerTurn.PLAYER1:
        g.currentPlayer = g.p1
    else:
        g.currentPlayer = g.p2
    g.p1.hand = [olaf,olaf,olaf,pascal,pascal,wardrobe,wardrobe]
    g.p2.hand = [captain_hook,captain_hook,captain_hook,maleficent,maleficent,maleficent,simba]
    return g


class TestMulligan(unittest.TestCase):
    def test_p1_mulligan_different_choices(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,7)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),8)

    def test_p2_mulligan_different_choices(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER2)

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,7)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),8)

    def test_p1_mulligan_dulplicate_choices(self):
        g = mulligan_state_with_duplicate_cards_game(PlayerTurn.PLAYER1)

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,3)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),4)

    def test_p2_mulligan_duplicate_choices(self):
        g = mulligan_state_with_duplicate_cards_game(PlayerTurn.PLAYER2)

        actions = g.get_actions()
        num_mulls = sum(1 for _ in filter(lambda x: type(x) is MulliganAction, actions))
        num_pass = sum(1 for _ in filter(lambda x: type(x) is PassAction, actions))
        self.assertEqual(num_mulls,3)
        self.assertEqual(num_pass,1)
        self.assertEqual(len(actions),4)

    def test_p1_mulligan(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)
        # do the first mulligan
        g.process_action(MulliganAction(olaf))
        
        self.assertEqual(len(g.p1.hand), 6)
        self.assertEqual(len(g.p1.pending_mulligan), 1)
        self.assertEqual(len(g.p2.hand), 7)
        self.assertEqual(len(g.p2.pending_mulligan), 0)

    def test_p2_mulligan(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER2)

        # do the first mulligan
        g.process_action(MulliganAction(captain_hook))
        
        self.assertEqual(len(g.p1.hand), 7)
        self.assertEqual(len(g.p1.pending_mulligan), 0)
        self.assertEqual(len(g.p2.hand), 6)
        self.assertEqual(len(g.p2.pending_mulligan), 1)

    def test_p1_pass_mulligan(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)

        # immediately pass
        g.process_action(PassAction())

        # make sure we still have 7 cards and now its player 2 turn
        self.assertEqual(len(g.p1.hand), 7)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

    def test_p2_pass_mulligan(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER2)

        # immediately pass
        g.process_action(PassAction())
        
        # make sure we still have 7 cards and now its player 2 turn
        self.assertEqual(len(g.p1.hand), 7)
        # technically p1 also doesn't need to draw so we skip right to main phase
        self.assertEqual(g.phase, GamePhase.MAIN)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

    def test_p1_full_mulligan(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)

        actions = g.get_actions()
        # take all mulligan actions
        for a in filter(lambda x: type(x) is MulliganAction, actions):
            g.process_action(a)

        self.assertEqual(len(g.p1.hand), 0)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

        g.process_action(next(filter(lambda x: type(x) is PassAction, actions)))
        
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

    def test_p2_full_mulligan(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER2)

        actions = g.get_actions()
        # take all mulligan actions
        for a in filter(lambda x: type(x) is MulliganAction, actions):
            g.process_action(a)

        self.assertEqual(len(g.p2.hand), 0)
        self.assertEqual(g.phase, GamePhase.MULLIGAN)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

        g.process_action(PassAction())
        
        self.assertEqual(g.phase, GamePhase.DRAW_STARTING_HAND)
        # we skipped player 1 mulligan here so we don't need to draw cards
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

    def test_p1_skip_draw(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)

        # p1 pass all mulligans
        g.process_action(PassAction())

        # p2 does 1 mulligan
        g.process_action(MulliganAction(captain_hook))
        g.process_action(PassAction())
        
        # p2 needs to draw but p1 does not
        self.assertEqual(g.phase, GamePhase.DRAW_STARTING_HAND)
        self.assertEqual(g.player, PlayerTurn.PLAYER2)

        g.process_action(DrawAction(fire_the_cannons,1))

        # should be in main state now
        self.assertEqual(g.phase, GamePhase.MAIN)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

    def test_p2_skip_draw(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)

        # p1 does 1 mulligan
        g.process_action(MulliganAction(olaf))
        g.process_action(PassAction())

        # p2 pass all mulligans
        g.process_action(PassAction())
        
        # p1 needs to draw but p2 does not
        self.assertEqual(g.phase, GamePhase.DRAW_STARTING_HAND)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

        # draw 1 card
        g.process_action(DrawAction(friends_on_the_other_side,1))

        # p2 doesn't need to draw
        self.assertEqual(g.phase, GamePhase.MAIN)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)

    def test_p2_skip_both(self):
        g = mulligan_state_with_different_cards_game(PlayerTurn.PLAYER1)

        # p1 pass all mulligans
        g.process_action(PassAction())

        # p2 pass all mulligans
        g.process_action(PassAction())
        
        # neither p1 or p2 needs to draw
        self.assertEqual(g.phase, GamePhase.MAIN)
        self.assertEqual(g.player, PlayerTurn.PLAYER1)


if __name__ == '__main__':
    unittest.main()
