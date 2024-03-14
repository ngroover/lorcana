#!/usr/bin/python3

import unittest
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel,olaf,pascal,moana,mickey_mouse
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from action import FirstPlayerAction,PassAction,DrawAction
from test_support import test_contestants

class TestStartingHand(unittest.TestCase):
    def test_draw_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND

        actions = game.get_actions()
        self.assertEqual(29, len(actions))
        self.assertTrue(all(type(x) is DrawAction for x in actions))
        # chance to draw olaf is 3 out of 60
        olaf_draw_action = DrawAction(olaf,3)
        self.assertTrue(olaf_draw_action in actions)

    def test_draw_card_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND

        # draw an olaf
        olaf_draw_action = DrawAction(olaf,3)
        game.process_action(olaf_draw_action)

        # still 29 cards we can draw, but 1 less olaf
        actions = game.get_actions()
        self.assertEqual(29, len(actions))
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == olaf,actions)),1)    #ensure only 1 olaf draw action
        # we can only draw 2 olafs now
        olaf_draw_action = DrawAction(olaf,2)
        self.assertTrue(olaf_draw_action in actions)
        # our hand size is bigger
        self.assertTrue(len(game.p1.hand), 1)

    def test_draw_all_cards_first_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND

        cards_to_draw=[olaf,olaf,olaf,pascal,pascal,moana]
        for c in cards_to_draw:
            # here the weight doesn't matter going into
            # the process_action function so we can set it to 1
            game.process_action(DrawAction(c,1))

        self.assertEqual(game.p1.hand.count(olaf), 3)
        self.assertEqual(game.p1.hand.count(pascal), 2)
        self.assertEqual(game.p1.hand.count(moana), 1)

        # make sure we can't draw pascal or olaf
        actions = game.get_actions()
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == olaf,actions)),0)    #ensure 0 olaf draw action
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == olaf,actions)),0)    #ensure 0 pascal draw action

        # draw last card
        game.process_action(DrawAction(mickey_mouse,1))
        self.assertEqual(game.p1.hand.count(mickey_mouse), 1)

        #still drawing but now it's player 2s turn
        self.assertEqual(game.phase, GamePhase.DRAW_STARTING_HAND)
        self.assertEqual(game.player, PlayerTurn.PLAYER2) 






if __name__ == '__main__':
    unittest.main()
