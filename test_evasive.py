#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder,amber_amethyst,sapphire_steel,jetsam,ruby_emerald,pongo
from game import GamePhase,PlayerTurn

class TestEvasive(unittest.TestCase):
    def test_cannot_challenge_into_evasive(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([jetsam], [captain_hook])\
                .quest(jetsam).pass_turn()

        actions = g.game.get_actions()

        # make sure captain_hook cannot challenge jetsam here because he's evasive
        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == captain_hook, actions))))

    def test_can_challenge_only_non_evasive(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([jetsam,olaf], [captain_hook])\
                .quest(jetsam).quest(olaf).pass_turn()

        actions = g.game.get_actions()

        # captain hook can still challenge here because there's an olaf
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == captain_hook, actions))))

    def test_can_challenge_non_evasive_correct_targets(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([jetsam,olaf], [captain_hook])\
                .quest(jetsam).quest(olaf).pass_turn()\
                .challenge(captain_hook)

        actions = g.game.get_actions()

        # Make sure captain hook can only challenge the olaf
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeTargetAction, actions))))

    def test_evasive_can_challenge_into_evasive(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,ruby_emerald)\
                .setup_cards([jetsam], [pongo])\
                .quest(jetsam).pass_turn()

        actions = g.game.get_actions()

        # pongo can challenge jetsam because he's evasive
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeAction and \
                        x.card == pongo, actions))))

    def test_can_challenge_non_evasive_correct_targets(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,ruby_emerald)\
                .setup_cards([jetsam,olaf], [pongo])\
                .quest(jetsam).quest(olaf).pass_turn()\
                .challenge(pongo)

        actions = g.game.get_actions()

        # pongo can challenge olaf and jetsam because he's evasive
        self.assertEqual(2, len(list(
                filter(lambda x: type(x) is ChallengeTargetAction, actions))))

        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeTargetAction and x.card == olaf, actions))))

        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is ChallengeTargetAction and x.card == jetsam, actions))))


if __name__ == '__main__':
    unittest.main()
