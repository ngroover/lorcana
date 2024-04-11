#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder
from game import GamePhase

class TestDuplicates(unittest.TestCase):
    def test_different_quester_choices(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand2().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_flounder().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .flounder_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(2, g.game.p1.in_play_characters[0].damage)
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
        
        g.init_game().draw_opening_hand2().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_flounder().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .flounder_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(2, g.game.p1.in_play_characters[0].damage)
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
        
        g.init_game().draw_opening_hand2().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_flounder().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .flounder_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(2, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[0].ready)

        g.olaf_challenge_flounder(0)

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
        
        g.init_game().draw_opening_hand2().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_flounder().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .flounder_challenge_olaf().pass_turn()\
                .quest_olaf().quest_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(2, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)
        self.assertFalse(g.game.p1.in_play_characters[0].ready)
        self.assertFalse(g.game.p1.in_play_characters[1].ready)

        g.challenge(flounder)

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
        self.assertTrue(g.game.p1.in_play_characters[0].ready)
        self.assertTrue(g.game.p1.in_play_characters[1].ready)


        actions = g.game.get_actions()

        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == olaf, actions))))

    def test_challenge_damaged_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand2().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_flounder().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .flounder_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(2, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[0].ready)

        g.olaf_challenge_flounder(0)

        # olaf actually dies here so we will check for that
        self.assertEqual(1, len(g.game.p1.in_play_characters))
        # this olaf is now the undamaged one
        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)


    def test_challenge_full_health_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand2().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_flounder().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()\
                .flounder_challenge_olaf().pass_turn()

        # one olaf has damage one doesn't
        self.assertEqual(2, g.game.p1.in_play_characters[0].damage)
        self.assertEqual(0, g.game.p1.in_play_characters[1].damage)

        self.assertTrue(g.game.p1.in_play_characters[1].ready)

        g.olaf_challenge_flounder(1)

        self.assertFalse(g.game.p1.in_play_characters[1].ready)
        self.assertEqual(2, g.game.p1.in_play_characters[1].damage)

    def test_duplicate_dinglehoppers(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .pass_turn()\
                .ink_olaf().play_dinglehopper().play_dinglehopper()

        actions = g.game.get_actions()
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is TriggeredAbilityAction and \
                        x.card == dinglehopper and \
                        x.ability == HealingTriggeredAbility(), actions))))

    def test_trigger_two_dinglehoppers(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .pass_turn()\
                .ink_olaf().play_dinglehopper().play_dinglehopper()

        # only one action because its the same either dinglehopper you pick
        actions = g.game.get_actions()
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is TriggeredAbilityAction and \
                        x.card == dinglehopper and \
                        x.ability == HealingTriggeredAbility(), actions))))

        g.use_dinglehopper().target_olaf()

        # we should be able to use the second dinglehopper
        actions = g.game.get_actions()
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is TriggeredAbilityAction and \
                        x.card == dinglehopper and \
                        x.ability == HealingTriggeredAbility(), actions))))

        g.use_dinglehopper().target_olaf()

        # no more dinglehoppers left
        actions = g.game.get_actions()
        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is TriggeredAbilityAction and \
                        x.card == dinglehopper and \
                        x.ability == HealingTriggeredAbility(), actions))))





if __name__ == '__main__':
    unittest.main()
