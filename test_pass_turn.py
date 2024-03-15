#!/usr/bin/python3

import unittest
from test_support import main_state_with_half_inkables_game
from action import InkAction,PlayCardAction,PassAction
from decklists import olaf,pascal,CharacterCard

class TestPassTurn(unittest.TestCase):
    def test_pass_turn_choice(self):
        g = main_state_with_half_inkables_game()

        actions = g.get_actions()
        self.assertTrue(any(type(x) is PassAction for x in actions))

if __name__ == '__main__':
    unittest.main()
