#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,amber_amethyst, sapphire_steel
from game import GamePhase

class TestChallenger(unittest.TestCase):
    def test_captain_hook_challenger(self):
        g = GameGenerator()
        
        g.init_game(amber_amethyst, sapphire_steel)\
                .setup_cards([olaf],[captain_hook])\
                .quest(olaf).pass_turn_draw()

        self.assertEqual(1, len(g.game.p1.in_play_characters))

        g.hook_challenge_olaf().pass_turn_draw()

        #olaf got banished so we should have no characters in play
        self.assertEqual(0, len(g.game.p1.in_play_characters))

if __name__ == '__main__':
    unittest.main()
