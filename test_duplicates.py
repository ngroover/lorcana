#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf
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

        print(f'actions {actions}')
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

        print(f'actions {actions}')
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is QuestAction and \
                        x.card == olaf, actions))))


    def test_quest_damaged_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()

    def test_quest_damaged_olaf(self):
        g = GameGenerator()
        
        g.init_game().draw_opening_hand().pass_mulligan()\
                .ink_pascal().play_olaf().pass_turn()\
                .ink_hook().play_hook().pass_turn()\
                .ink_olaf().play_olaf().quest_olaf().pass_turn()



if __name__ == '__main__':
    unittest.main()
