#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder,amber_amethyst,sapphire_steel,jetsam,ruby_emerald,pongo,pascal
from game import GamePhase,PlayerTurn

class TestEvasive(unittest.TestCase):
    def test_cannot_challenge_pascal_with_olaf_on_board(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([pascal,olaf], [captain_hook])\
                .quest(pascal).pass_turn()

        actions = g.game.get_actions()

        # make sure captain_hook cannot challenge pascal here because he's evasive
        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == captain_hook, actions))))

if __name__ == '__main__':
    unittest.main()
