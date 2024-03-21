#!/usr/bin/python3

import unittest
from basic_game_generator import BasicGameGenerator
from decklists import olaf
from action import InkAction


class TestTurnReset(unittest.TestCase):
    def test_characters_ready(self):
        g = BasicGameGenerator()
        g.init_game().draw_opening_hand().pass_mulligan() \
                .play_olaf_pass().p2_pass()

        self.assertEqual(1, len(g.game.p1.in_play_characters))
        self.assertEqual(olaf, g.game.p1.in_play_characters[0].card)

        g.quest_olaf_pass()

        self.assertEqual(1, len(g.game.p1.in_play_characters))
        self.assertEqual(olaf, g.game.p1.in_play_characters[0].card)
        self.assertFalse(g.game.p1.in_play_characters[0].ready)

        g.p2_pass()

        self.assertEqual(1, len(g.game.p1.in_play_characters))
        self.assertEqual(olaf, g.game.p1.in_play_characters[0].card)
        self.assertTrue(g.game.p1.in_play_characters[0].ready)

    def test_characters_dry(self):
        g = BasicGameGenerator()
        g.init_game().draw_opening_hand().pass_mulligan().play_olaf()

        self.assertEqual(1, len(g.game.p1.in_play_characters))
        self.assertEqual(olaf, g.game.p1.in_play_characters[0].card)
        self.assertFalse(g.game.p1.in_play_characters[0].dry)

    def test_ink_ready(self):
        g = BasicGameGenerator()
        g.init_game().draw_opening_hand().pass_mulligan() \
                .play_olaf()

        self.assertEqual(1, g.game.p1.exerted_ink)
        self.assertEqual(0, g.game.p1.ready_ink)

        g.p1_pass()
        g.p2_pass()

        self.assertEqual(0, g.game.p1.exerted_ink)
        self.assertEqual(1, g.game.p1.ready_ink)
    
    def test_back_to_back_ink(self):
        g = BasicGameGenerator()
        g.init_game().draw_opening_hand().pass_mulligan()


        self.assertTrue(any(type(x) is InkAction for x in g.game.get_actions()))
        g.ink_olaf()

        self.assertFalse(any(type(x) is InkAction for x in g.game.get_actions()))

        g.p1_pass()

        self.assertTrue(any(type(x) is InkAction for x in g.game.get_actions()))



if __name__ == '__main__':
    unittest.main()
