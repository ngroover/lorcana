#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook
from game import GamePhase

class TestDuplicates(unittest.TestCase):
    def test_different_quester_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()
        #NOTE: once we add challenger this test will break because captain hook
        # kills olaf

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        actions = g.game.get_actions()

        self.assertEqual(2, len(list(
                filter(lambda x: type(x) is QuestAction and \
                        x.card == olaf, actions))))

    def test_same_quester_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .pass_turn()

        # both olafs don't have damage
        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        actions = g.game.get_actions()

        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is QuestAction and \
                        x.card == olaf, actions))))


    def test_quest_damaged_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[0].ready)

        g.quest(olaf, 0)

        self.assertFalse(g.game.p1.in_play_characters[0].ready)

    def test_quest_full_health_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[1].ready)

        g.quest(olaf, 1)

        self.assertFalse(g.game.p1.in_play_characters[1].ready)

    def test_different_challenger_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()
        #NOTE: once we add challenger this test will break because captain hook
        # kills olaf

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        actions = g.game.get_actions()

        self.assertEqual(2, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == olaf, actions))))

    def test_same_challenger_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .quest_hook().pass_turn()

        # both olafs don't have damage
        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        actions = g.game.get_actions()

        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == olaf, actions))))

    def test_challenge_damaged_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[0].ready)

        g.olaf_challenge_hook(0)

        self.assertFalse(g.game.p1.in_play_characters[0].ready)


    def test_challenge_full_health_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[1].ready)

        g.olaf_challenge_hook(1)

        self.assertFalse(g.game.p1.in_play_characters[1].ready)

    def test_different_challenger_target_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()\
                .quest_olaf().quest_olaf().pass_turn()
        #NOTE: once we add challenger this test will break because captain hook
        # kills olaf

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)
        self.assertFalse(g.game.p1.in_play_characters[0].ready)
        self.assertFalse(g.game.p1.in_play_characters[1].ready)

        g.challenge(captain_hook)

        actions = g.game.get_actions()

        self.assertEqual(2, len(list(
                filter(lambda x: type(x) is ChallengeTargetAction and \
                        x.card == olaf, actions))))

    def test_same_challenger_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .quest_hook().pass_turn()

        # both olafs don't have damage
        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)
        self.assertFalse(g.game.p1.in_play_characters[0].ready)
        self.assertFalse(g.game.p1.in_play_characters[1].ready)


        actions = g.game.get_actions()

        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == olaf, actions))))

    def test_challenge_damaged_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[0].ready)

        g.olaf_challenge_hook(0)

        self.assertFalse(g.game.p1.in_play_characters[0].ready)


    def test_challenge_full_health_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .hook_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[1].ready)

        g.olaf_challenge_hook(1)

        self.assertFalse(g.game.p1.in_play_characters[1].ready)






if __name__ == '__main__':
    unittest.main()
