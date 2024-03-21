#!/usr/bin/python3

import unittest
from basic_game_generator import BasicGameGenerator
from decklists import olaf


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
        pass
    
    def test_back_to_back_ink(self):
        pass


if __name__ == '__main__':
    unittest.main()
