#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder,amber_amethyst,sapphire_steel,jetsam,ruby_emerald,pongo,pascal,moana,ariel
from game import GamePhase,PlayerTurn

class TestBanish(unittest.TestCase):
    def test_character_defender_banish(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([olaf], [captain_hook])\
                .quest(olaf).pass_turn_draw()\
                .challenge(captain_hook).challenge_target(olaf)

        char_list = list(filter(lambda x: x.card == olaf, g.game.p1.in_play_characters))

        self.assertEqual(0, len(char_list))

        discard_pile = g.game.p1.discard

        self.assertEqual(1, len(discard_pile))

if __name__ == '__main__':
    unittest.main()
