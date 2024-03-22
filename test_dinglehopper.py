#!/usr/bin/python3

import unittest
from dinglehopper_game_generator import DinglehopperGameGenerator

class TestDinglehopper(unittest.TestCase):
    def test_play_dinglehopper(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand()\
                .pass_mulligan().ink_olaf().play_olaf()


if __name__ == '__main__':
    unittest.main()
