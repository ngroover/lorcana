#!/usr/bin/python3

import unittest
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel,olaf,pascal,moana,mickey_mouse,captain_hook,maleficent,scar,wardrobe,dinglehopper,stitch
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
                filter(lambda x: x.card == pascal,actions)),0)    #ensure 0 pascal draw action

        # draw last card
        game.process_action(DrawAction(mickey_mouse,1))
        self.assertEqual(game.p1.hand.count(mickey_mouse), 1)

        #still drawing but now it's player 2s turn
        self.assertEqual(game.phase, GamePhase.DRAW_STARTING_HAND)
        self.assertEqual(game.player, PlayerTurn.PLAYER2) 

    def test_draw_second_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND
        game.player = PlayerTurn.PLAYER2
        game.currentPlayer = game.p2

        actions = game.get_actions()
        self.assertEqual(29, len(actions))
        self.assertTrue(all(type(x) is DrawAction for x in actions))
        # chance to draw hook is 3 out of 60
        hook_draw_action = DrawAction(captain_hook,3)
        self.assertTrue(hook_draw_action in actions)

    def test_draw_card_second_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND
        game.player = PlayerTurn.PLAYER2
        game.currentPlayer = game.p2

        # draw a hook
        hook_draw_action = DrawAction(captain_hook,3)
        game.process_action(hook_draw_action)

        # still 29 cards we can draw, but 1 less olaf
        actions = game.get_actions()
        self.assertEqual(29, len(actions))
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == captain_hook,actions)),1)    #ensure only 1 captain hook draw action
        # we can only draw 2 captain hooks now
        hook_draw_action = DrawAction(captain_hook,2)
        self.assertTrue(hook_draw_action in actions)
        # our hand size is bigger
        self.assertTrue(len(game.p2.hand), 1)

    def test_draw_all_cards_second_player(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND
        game.player = PlayerTurn.PLAYER2
        game.currentPlayer = game.p2
        # give p1 a hand so they dont need to draw
        game.p1.hand = [olaf,pascal,moana,mickey_mouse,wardrobe,dinglehopper,stitch]

        cards_to_draw=[captain_hook,captain_hook,captain_hook,maleficent,maleficent,maleficent]
        for c in cards_to_draw:
            # here the weight doesn't matter going into
            # the process_action function so we can set it to 1
            game.process_action(DrawAction(c,1))

        self.assertEqual(game.p2.hand.count(captain_hook), 3)
        self.assertEqual(game.p2.hand.count(maleficent), 3)

        # make sure we can't draw captain_hook or maleficent anymore
        actions = game.get_actions()
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == captain_hook,actions)),0)    #ensure 0 captain_hook draw action
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == maleficent,actions)),0)    #ensure 0 maleficent draw action

        # draw last card
        game.process_action(DrawAction(scar,1))
        self.assertEqual(game.p2.hand.count(scar), 1)

        # now we are in the mulligan phase
        self.assertEqual(game.phase, GamePhase.MULLIGAN)
        self.assertEqual(game.player, PlayerTurn.PLAYER1) 

    def test_draw_all_cards_second_player_after_mulligan(self):
        c = test_contestants()
        game = Game(c[0],c[1],RandomController('env'))
        game.phase = GamePhase.DRAW_STARTING_HAND
        game.player = PlayerTurn.PLAYER2
        game.currentPlayer = game.p2
        game.mulligan_finished = True
        # give p1 a hand so they dont need to draw
        game.p1.hand = [olaf,pascal,moana,mickey_mouse,wardrobe,dinglehopper,stitch]

        cards_to_draw=[captain_hook,captain_hook,captain_hook,maleficent,maleficent,maleficent]
        for c in cards_to_draw:
            # here the weight doesn't matter going into
            # the process_action function so we can set it to 1
            game.process_action(DrawAction(c,1))

        self.assertEqual(game.p2.hand.count(captain_hook), 3)
        self.assertEqual(game.p2.hand.count(maleficent), 3)

        # make sure we can't draw captain_hook or maleficent anymore
        actions = game.get_actions()
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == captain_hook,actions)),0)    #ensure 0 captain_hook draw action
        self.assertEqual(sum(1 for _ in 
                filter(lambda x: x.card == maleficent,actions)),0)    #ensure 0 maleficent draw action

        # draw last card
        game.process_action(DrawAction(scar,1))
        self.assertEqual(game.p2.hand.count(scar), 1)

        # now we are in the main phase because we already mulliganed
        self.assertEqual(game.phase, GamePhase.MAIN)
        self.assertEqual(game.player, PlayerTurn.PLAYER1) 







if __name__ == '__main__':
    unittest.main()
