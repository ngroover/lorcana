#!/usr/bin/python3

import unittest
from test_support import main_state_with_some_characters_in_play,main_state_with_some_characters_in_play_p2,main_state_with_some_characters_in_play_p1
from action import InkAction,PlayCardAction,ChallengeAction,ChallengeTargetAction
from decklists import olaf,pascal,CharacterCard,flounder,captain_hook,mickey_mouse_true_friend,kristoff
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

    def test_challenge_targets(self):
        g = main_state_with_some_characters_in_play()

        g.process_action(ChallengeAction(olaf))

        actions = g.get_actions()

        # should be all the playable characters
        challenge_characters = list(filter(lambda x: 
                    type(x) is ChallengeTargetAction and
                    type(x.card) is CharacterCard, actions))
        
        # the only challengable target is flounder since he's exerted
        self.assertEqual(1,len(challenge_characters))
        self.assertEqual(flounder, challenge_characters[0].card)

    def test_challenge_both_live(self):
        g = main_state_with_some_characters_in_play()

        g.process_action(ChallengeAction(olaf))
        g.process_action(ChallengeTargetAction(flounder))

        olafs_in_play=list(filter(lambda x: x.card == olaf, g.p1.in_play_characters))
        self.assertEqual(1, len(olafs_in_play))
        flounders_in_play=list(filter(lambda x: x.card == flounder, g.p2.in_play_characters))
        self.assertEqual(1, len(flounders_in_play))

        self.assertEqual(2, olafs_in_play[0].damage)
        self.assertEqual(1, flounders_in_play[0].damage)
        self.assertFalse(olafs_in_play[0].ready)

    def test_challenge_challenger_dies(self):
        g = main_state_with_some_characters_in_play()

        g.process_action(ChallengeAction(pascal))
        g.process_action(ChallengeTargetAction(flounder))

        pascals_in_play=list(filter(lambda x: x.card == pascal, g.p1.in_play_characters))
        self.assertEqual(0, len(pascals_in_play))
        flounders_in_play=list(filter(lambda x: x.card == flounder, g.p2.in_play_characters))
        self.assertEqual(1, len(flounders_in_play))
        self.assertEqual(1, flounders_in_play[0].damage)

        self.assertEqual(1, g.p1.discard.count(pascal))
        self.assertEqual(GamePhase.MAIN, g.phase)

    def test_challenge_challengee_dies(self):
        g = main_state_with_some_characters_in_play_p2()

        g.process_action(ChallengeAction(flounder))
        g.process_action(ChallengeTargetAction(pascal))

        flounders_in_play=list(filter(lambda x: x.card == flounder, g.p2.in_play_characters))
        self.assertEqual(1, len(flounders_in_play))
        self.assertEqual(1, flounders_in_play[0].damage)
        pascal_in_play=list(filter(lambda x: x.card == pascal, g.p1.in_play_characters))
        self.assertEqual(0, len(pascal_in_play))

        self.assertEqual(1, g.p1.discard.count(pascal))
        self.assertEqual(GamePhase.MAIN, g.phase)

    def test_challenge_both_die(self):
        g = main_state_with_some_characters_in_play_p1()

        g.process_action(ChallengeAction(mickey_mouse_true_friend))
        g.process_action(ChallengeTargetAction(kristoff))

        mickey_in_play=list(filter(lambda x: x.card == mickey_mouse_true_friend, g.p1.in_play_characters))
        self.assertEqual(0, len(mickey_in_play))
        kristoff_in_play=list(filter(lambda x: x.card == kristoff, g.p2.in_play_characters))
        self.assertEqual(0, len(kristoff_in_play))

        self.assertEqual(1, g.p1.discard.count(mickey_mouse_true_friend))
        self.assertEqual(1, g.p2.discard.count(kristoff))
        self.assertEqual(GamePhase.MAIN, g.phase)


if __name__ == '__main__':
    unittest.main()
