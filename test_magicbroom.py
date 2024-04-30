#!/usr/bin/python3

import unittest
from game_generator import GameGenerator
from action import PlayCardAction,TriggeredAbilityAction,AbilityTargetAction,QuestAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility
from decklists import dinglehopper,olaf,captain_hook,flounder,amber_amethyst,sapphire_steel,jetsam,ruby_emerald,pongo,pascal,moana,ariel,magic_broom
from game import GamePhase,PlayerTurn

class TestMagicBroom(unittest.TestCase):
    def test_magic_broom_on_play_ability(self):
        g = GameGenerator()

        g.init_game(amber_amethyst,sapphire_steel)\
                .setup_cards([olaf], [captain_hook], 3)\
                .quest(olaf).pass_turn_draw()\
                .challenge(captain_hook).challenge_target(olaf)

        g.pass_turn().draw_card(magic_broom).play_card(magic_broom)

        

if __name__ == '__main__':
    unittest.main()
