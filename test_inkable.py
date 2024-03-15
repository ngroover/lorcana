#!/usr/bin/python3

import unittest
from test_support import main_state_with_half_inkables_game
from decklists import olaf,pascal

class TestInkables(unittest.TestCase):
    def test_inkable_choices(self):
        g = main_state_with_half_inkables_game()

        actions = g.get_actions()
        expected_inkable_cards = set([olaf,pascal])
        actual_inkable_cards = set(map(lambda y: y.card,
                filter(lambda x: type(x) is InkAction, actions)))
        
        self.assertEqual(expected_inkable_cards,actual_inkable_cards)


if __name__ == '__main__':
    unittest.main()
