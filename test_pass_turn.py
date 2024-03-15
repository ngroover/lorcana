#!/usr/bin/python3

import unittest
from test_support import main_state_with_half_inkables_game
from action import InkAction,PlayCardAction,PassAction
from decklists import olaf,pascal,CharacterCard,captain_hook
from game import GamePhase,PlayerTurn
from inplay_character import InPlayCharacter

class TestPassTurn(unittest.TestCase):
    def test_pass_turn_choice(self):
        g = main_state_with_half_inkables_game()

        actions = g.get_actions()
        self.assertTrue(any(type(x) is PassAction for x in actions))

    def test_pass_turn_choice(self):
        g = main_state_with_half_inkables_game()

        g.process_action(PassAction())

        self.assertEqual(GamePhase.DRAW_PHASE, g.phase)
        self.assertEqual(PlayerTurn.PLAYER2, g.player)

    def test_pass_turn_ready_characters(self):
        g = main_state_with_half_inkables_game()
        in_play_hook = InPlayCharacter(captain_hook)
        in_play_hook.ready = False

        g.p2.in_play_characters.append(in_play_hook)
        g.process_action(PassAction())

        self.assertEqual(1, len(g.p2.in_play_characters))
        self.assertTrue(g.p2.in_play_characters[0].ready)

if __name__ == '__main__':
    unittest.main()