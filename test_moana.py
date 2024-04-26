#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder,amber_amethyst,sapphire_steel,jetsam,ruby_emerald,pongo,pascal,moana,ariel
from game import GamePhase,PlayerTurn

class TestMoana(unittest.TestCase):
    def test_quest_ready_princess(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([moana,ariel], [captain_hook])\
                .quest(ariel)

        inplay_ariel = next(filter(lambda x: x.card == ariel, g.game.p1.in_play_characters))
        inplay_moana = next(filter(lambda x: x.card == moana, g.game.p1.in_play_characters))

        self.assertFalse(inplay_ariel.ready)

        g.quest(moana)

        #ariel should be ready she's a princess
        self.assertTrue(inplay_ariel.ready)
        self.assertFalse(inplay_moana.ready)


if __name__ == '__main__':
    unittest.main()
