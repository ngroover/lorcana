#!/usr/bin/python3

import unittest
from test_support import main_state_with_half_inkables_game
from action import InkAction,PlayCardAction,PassAction,DrawAction
from decklists import olaf,pascal,CharacterCard,captain_hook,rafiki
from game import GamePhase,PlayerTurn
from inplay_character import InPlayCharacter

class TestDrawPhase(unittest.TestCase):
    def test_draw_phase_choices(self):
        g = main_state_with_half_inkables_game()
        g.phase= GamePhase.DRAW_PHASE

        actions = g.get_actions()
        self.assertEqual(26, len(actions))
        draw_actions = sum(1 for _ in filter(lambda x: type(x)
                        is DrawAction, actions))
        self.assertEqual(26, draw_actions)

    def test_draw_phase_draw(self):
        g = main_state_with_half_inkables_game()
        g.phase= GamePhase.DRAW_PHASE

        g.process_action(DrawAction(rafiki))

        # still player 1's turn
        self.assertEqual(PlayerTurn.PLAYER1, g.player)
        self.assertEqual(GamePhase.MAIN, g.phase)
        # hand contains rafiki
        self.assertTrue(any(x == rafiki for x in g.p1.hand))



if __name__ == '__main__':
    unittest.main()
