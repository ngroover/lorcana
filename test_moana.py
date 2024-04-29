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

    def test_quest_only_princess_ready(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([moana,ariel,olaf], [captain_hook])\
                .quest(ariel).quest(olaf)

        inplay_ariel = next(filter(lambda x: x.card == ariel, g.game.p1.in_play_characters))
        inplay_moana = next(filter(lambda x: x.card == moana, g.game.p1.in_play_characters))
        inplay_olaf = next(filter(lambda x: x.card == olaf, g.game.p1.in_play_characters))

        self.assertFalse(inplay_olaf.ready)

        g.quest(moana)

        #olaf should still be exerted. he's not a princess
        self.assertFalse(inplay_olaf.ready)

    def test_quest_princesses_cannot_quest(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([moana,ariel,olaf], [captain_hook])\
                .quest(ariel).quest(olaf)

        inplay_ariel = next(filter(lambda x: x.card == ariel, g.game.p1.in_play_characters))

        self.assertFalse(inplay_ariel.ready)

        g.quest(moana)

        # ariel is ready but she cannot quest
        self.assertTrue(inplay_ariel.ready)

        actions = g.game.get_actions()

        self.assertEqual(0, len(list(
                filter(lambda x: type(x) is QuestAction and \
                        x.card == ariel, actions))))

    def test_quest_princesses_can_eventually_quest(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([moana,ariel,olaf], [captain_hook])\
                .quest(ariel).quest(olaf)

        inplay_ariel = next(filter(lambda x: x.card == ariel, g.game.p1.in_play_characters))

        g.quest(moana).pass_turn_draw().pass_turn_draw()

        actions = g.game.get_actions()

        # ariel is ready she can quest now next turn
        self.assertTrue(inplay_ariel.ready)
        self.assertEqual(1, len(list(
                filter(lambda x: type(x) is QuestAction and \
                        x.card == ariel, actions))))




if __name__ == '__main__':
    unittest.main()
