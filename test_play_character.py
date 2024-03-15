#!/usr/bin/python3

import unittest
from test_support import main_state_with_half_inkables_game
from action import InkAction,PlayCardAction
from decklists import olaf,pascal,CharacterCard

class TestPlayCharacters(unittest.TestCase):
    def test_no_play_character_choices(self):
        g = main_state_with_half_inkables_game()

        actions = g.get_actions()
        # should be all the playable characters
        playable_character_cards = sum(1 for _ in
                filter(lambda x: type(x) is PlayCardAction and
                    type(x.card) is CharacterCard, actions))
        
        self.assertEqual(0,playable_character_cards)

    def test_play_character_choices(self):
        g = main_state_with_half_inkables_game()
        g.p1.inkwell = 1

        actions = g.get_actions()
        # both olaf and pascal cost 1
        expected_playable_chars = set([olaf,pascal])
        actual_playable_chars = set(map(lambda y: y.card,
                filter(lambda x: type(x) is PlayCardAction and
                        type(x.card) is CharacterCard, actions)))

        self.assertEqual(expected_playable_chars, actual_playable_chars)



if __name__ == '__main__':
    unittest.main()
