#!/usr/bin/python3

import unittest
from test_support import main_state_with_some_characters_in_play
from action import InkAction,PlayCardAction,ChallengeAction
from decklists import olaf,pascal,CharacterCard
from game import GamePhase

class TestChallenging(unittest.TestCase):
    def test_challenge_choices(self):
        g = main_state_with_some_characters_in_play()

        actions = g.get_actions()
        # should be all the playable characters
        challenge_characters = sum(1 for _ in
                filter(lambda x: type(x) is ChallengeAction and
                    type(x.card) is CharacterCard, actions))
        
        # olaf and pascal can challenge flounder
        self.assertEqual(2,challenge_characters)

    def test_start_challenge(self):
        g = main_state_with_some_characters_in_play()

        g.process_action(ChallengeAction(olaf))

        self.assertEqual(GamePhase.CHALLENGING, g.phase)
        self.assertTrue(g.current_challenger != None)
        self.assertEqual(g.current_challenger.card, olaf)



if __name__ == '__main__':
    unittest.main()
