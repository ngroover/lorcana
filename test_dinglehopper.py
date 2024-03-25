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



if __name__ == '__main__':
    unittest.main()
