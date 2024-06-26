#!/usr/bin/python3

import unittest
from test_support import main_state_with_half_inkables_game
from action import InkAction
from decklists import olaf,pascal

class TestInkables(unittest.TestCase):
    def test_inkable_choices(self):
        g = main_state_with_half_inkables_game()

        actions = g.get_actions()
        expected_inkable_cards = set([olaf,pascal])
        actual_inkable_cards = set(map(lambda y: y.card,
                filter(lambda x: type(x) is InkAction, actions)))
        
        self.assertEqual(expected_inkable_cards,actual_inkable_cards)

    def test_ink_card(self):
        g = main_state_with_half_inkables_game()

        # ink an olaf
        g.process_action(InkAction(olaf))

        olafs_in_hand=g.p1.hand.count(olaf)
        self.assertEqual(2,olafs_in_hand)
        self.assertEqual(1,g.p1.ready_ink)

    def test_cant_ink_twice(self):
        g = main_state_with_half_inkables_game()

        # ink an olaf
        g.process_action(InkAction(olaf))

        actions = g.get_actions()
        ink_options = sum(1 for _ in filter(lambda x: type(x) is InkAction, actions))

        # verify we can't ink again this turn
        self.assertEqual(0,ink_options)


if __name__ == '__main__':
    unittest.main()
