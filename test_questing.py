#!/usr/bin/python3

import unittest
from test_support import main_state_with_some_characters_in_play
from action import InkAction,PlayCardAction,PassAction,DrawAction,QuestAction
from decklists import olaf,pascal,CharacterCard,captain_hook,rafiki
from game import GamePhase,PlayerTurn
from inplay_character import InPlayCharacter


class TestQuesting(unittest.TestCase):
    def test_quest_actions(self):
        g = main_state_with_some_characters_in_play()

        expected_questable=set([olaf,pascal])
        actions = g.get_actions()

        actual_questable = set(map(lambda x: x.card,
            filter(lambda y: type(y) is QuestAction, actions)))

        self.assertEqual(expected_questable, actual_questable)

if __name__ == '__main__':
    unittest.main()
