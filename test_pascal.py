#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder,amber_amethyst,sapphire_steel,jetsam,ruby_emerald,pongo,pascal
from game import GamePhase,PlayerTurn

class TestPascal(unittest.TestCase):
    def test_cannot_challenge_pascal_with_olaf_on_board(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([pascal,olaf], [captain_hook])\
                .quest(pascal).pass_turn_draw()

        actions = g.game.get_actions()

        # make sure captain_hook cannot challenge pascal here because he's evasive
        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == captain_hook, actions))))

    def test_can_challenge_pascal_by_himself(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([pascal], [captain_hook])\
                .quest(pascal).pass_turn_draw()

        actions = g.game.get_actions()

        # make sure captain_hook can challenge pascal here because he's not evasive
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == captain_hook, actions))))

    def test_pascal_cannot_challenge_pascal(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,amber_amethyst)\
                .setup_cards([pascal,pascal], [pascal])\
                .quest(pascal).quest(pascal).pass_turn_draw()

        actions = g.game.get_actions()

        # the solo pascal cannot challenge the 2 pascal side
        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == pascal, actions))))

    def test_pascal_can_challenge_pascal(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,amber_amethyst)\
                .setup_cards([pascal,pascal], [pascal,pascal])\
                .quest(pascal).quest(pascal).pass_turn_draw()

        actions = g.game.get_actions()

        # the solo pascal cannot challenge the 2 pascal side
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == pascal, actions))))

if __name__ == '__main__':
    unittest.main()
