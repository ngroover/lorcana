#!/usr/bin/python3

import unittest
from dinglehopper_game_generator import DinglehopperGameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper
from game import GamePhase

class TestDinglehopper(unittest.TestCase):
    def test_can_play_dinglehopper(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf()

        actions = g.game.get_actions()
        self.assertTrue(any(type(x) is PlayCardAction and x.card == dinglehopper for x in actions))

    def test_choose_play_dinglehopper(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_dinglehopper()

        self.assertEqual(1,len(g.game.p1.in_play_items))
        self.assertEqual(dinglehopper,g.game.p1.in_play_items[0].card)
        self.assertTrue(g.game.p1.in_play_items[0].ready)
        
    # you can play dingle hopper right away even with no targets
    def test_choose_dinglehopper_ability(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_dinglehopper()

        actions = g.game.get_actions()
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is TriggeredAbilityAction and \
                        x.card == dinglehopper and \
                        x.ability == HealingTriggeredAbility(), actions))))

    def test_choose_dinglehopper_target(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .play_dinglehopper().use_dinglehopper()

        actions = g.game.get_actions()
        self.assertEqual(2, len(list(
                filter(lambda x: type(x) is AbilityTargetAction, actions))))
        self.assertEqual(GamePhase.CHOOSE_TARGET, g.game.phase)

    def test_perform_dinglehopper_do_nothing(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .play_dinglehopper()

        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)

        g.use_dinglehopper().target_olaf()

        self.assertEqual(0, g.game.p1.in_play_characters[0].damage) # still 0 damage

    def test_cant_use_dinglehopper_when_exerted(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .play_dinglehopper()

        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)

        g.use_dinglehopper().target_olaf()

        actions = g.game.get_actions()

        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is TriggeredAbilityAction and \
                        x.card == dinglehopper and \
                        x.ability == HealingTriggeredAbility(), actions))))

    def test_perform_dinglehopper_heal_self(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .play_dinglehopper().pass_turn()\
                .quest_hook().pass_turn()\
                .olaf_challenge_hook()

        self.assertEqual(1, g.game.p1.in_play_characters[0].damage)

        g.use_dinglehopper().target_olaf()

        # damage has been healed off
        self.assertEqual(0, g.game.p1.in_play_characters[0].damage)

    def test_perform_dinglehopper_heal_opponent(self):
        g = DinglehopperGameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_olaf().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .play_dinglehopper().pass_turn()\
                .quest_hook().pass_turn()\
                .olaf_challenge_hook()

        self.assertEqual(1, g.game.p2.in_play_characters[0].damage)

        g.use_dinglehopper().target_hook()

        # damage has been healed off hook
        self.assertEqual(0, g.game.p2.in_play_characters[0].damage)


if __name__ == '__main__':
    unittest.main()
