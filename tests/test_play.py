"""End-to-end tests: the AI, and a full game driven through the human interface."""

from __future__ import annotations

import contextlib
import io
import unittest

from helpers import new_game, put_character

from lorcana import carddb as db
from lorcana.actions import PassAction, QuestAction
from lorcana.ai import GreedyAI, SearchAI
from lorcana.cli import main, make_controller
from lorcana.controllers import HumanController, RandomController, render_board
from lorcana.decks import AMBER_AMETHYST, DECKLISTS, RUBY_EMERALD, SAPPHIRE_STEEL
from lorcana.game import Game


class HumanInterfaceTests(unittest.TestCase):
    def play_scripted_game(self, choice="1", deck1=AMBER_AMETHYST,
                           deck2=SAPPHIRE_STEEL, seed=3):
        """A 'human' who always picks the first offered option, versus the AI."""
        output = io.StringIO()
        human = HumanController("Scripted", input_fn=lambda prompt: choice,
                                output_fn=lambda *a: output.write(" ".join(map(str, a)) + "\n"))
        game = Game([("Scripted", deck1, human),
                     ("AI", deck2, SearchAI("AI", beam_width=3, rollouts=2))],
                    seed=seed)
        winner = game.run()
        return winner, game, output.getvalue()

    def test_a_full_game_can_be_played_through_the_menus(self):
        winner, game, text = self.play_scripted_game()
        self.assertIn(winner, (0, 1))
        self.assertTrue(game.players[winner].lore >= 20
                        or game.players[1 - winner].lost_to_empty_deck)
        # The interface showed a board and offered numbered options.
        self.assertIn("Your hand:", text)
        self.assertIn("1.", text)
        self.assertIn("lore", text)

    def test_board_rendering_mentions_both_players(self):
        game = new_game()
        put_character(game, 0, db.MOANA, damage=1)
        put_character(game, 1, db.PETER_PAN, ready=False)
        text = render_board(game, 0)
        self.assertIn("Moana", text)
        self.assertIn("Peter Pan", text)
        self.assertIn("Evasive", text)
        self.assertIn("exerted", text)

    def test_invalid_input_is_rejected_until_valid(self):
        replies = iter(["banana", "99", "0", "2"])
        chosen = []
        human = HumanController("H", input_fn=lambda prompt: next(replies),
                                output_fn=lambda *a: chosen.append(a))
        game = new_game()
        first = put_character(game, 0, db.OLAF)
        second = put_character(game, 0, db.MOANA)
        actions = [QuestAction(first.uid), QuestAction(second.uid)]
        picked = human.choose_action(game, game.players[0], actions)
        self.assertIn(picked, actions)


class ControllerFactoryTests(unittest.TestCase):
    def test_every_player_kind_can_be_created(self):
        for kind in ("human", "ai", "greedy", "random"):
            controller = make_controller(kind, kind.title(), seed=1)
            self.assertEqual(controller.name, kind.title())

    def test_difficulty_changes_the_search_budget(self):
        easy = make_controller("ai", "E", difficulty="easy")
        hard = make_controller("ai", "H", difficulty="hard")
        self.assertLess(easy.beam_width, hard.beam_width)


class CommandLineTests(unittest.TestCase):
    def run_main(self, argv):
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink):
            code = main(argv)
        return code, sink.getvalue()

    def test_list_decks_runs(self):
        code, text = self.run_main(["--list-decks"])
        self.assertEqual(code, 0)
        self.assertIn("Amber/Amethyst", text)
        self.assertIn("Dragon Fire", text)

    def test_bot_game_from_the_command_line(self):
        code, text = self.run_main(["--deck1", "1", "--deck2", "3", "--p1", "greedy",
                                    "--p2", "random", "--seed", "5", "--quiet"])
        self.assertEqual(code, 0)
        self.assertIn("wins", text)

    def test_series_of_bot_games(self):
        code, text = self.run_main(["--deck1", "2", "--deck2", "2", "--p1", "greedy",
                                    "--p2", "random", "--seed", "5", "--games", "3",
                                    "--quiet"])
        self.assertEqual(code, 0)
        self.assertIn("player 1:", text)
        self.assertIn("player 2:", text)
        results = [line for line in text.splitlines() if line.startswith("game ")]
        self.assertEqual(len(results), 3)          # one result line per game


class AITests(unittest.TestCase):
    def test_plans_are_made_of_legal_actions(self):
        game = new_game(hand1=[db.MOANA, db.OLAF], ink1=6)
        put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        put_character(game, 1, db.GOONS, ready=False)
        ai = SearchAI("AI", beam_width=3, rollouts=2)
        legal = game.legal_actions()
        action = ai.choose_action(game, game.players[0], legal)
        self.assertIn(action, legal)

    def test_search_does_not_mutate_the_real_game(self):
        game = new_game(hand1=[db.MOANA], ink1=6)
        put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        put_character(game, 1, db.GOONS, ready=False)
        before = (len(game.players[0].hand), game.players[0].lore,
                  len(game.players[0].characters), len(game.players[1].characters))
        ai = SearchAI("AI", beam_width=3, rollouts=2)
        ai.plan_turn(game, game.players[0])
        after = (len(game.players[0].hand), game.players[0].lore,
                 len(game.players[0].characters), len(game.players[1].characters))
        self.assertEqual(before, after)

    def test_ai_takes_a_lethal_line_when_one_exists(self):
        game = new_game(ink1=6)
        game.players[0].lore = 18
        put_character(game, 0, db.MOANA)          # 3 lore
        ai = SearchAI("AI", beam_width=3, rollouts=2)
        action = ai.choose_action(game, game.players[0], game.legal_actions())
        self.assertIsInstance(action, QuestAction)

    def test_ai_inks_a_card_every_turn_when_it_can(self):
        """Missing the ink drop is the classic engine-building blunder."""
        ai = SearchAI("AI")
        game = Game([("AI", AMBER_AMETHYST, ai),
                     ("R", SAPPHIRE_STEEL, RandomController("R", seed=2))],
                    seed=7)
        game.setup()
        for _ in range(8):
            if game.winner is not None:
                break
            game.play_turn()
            if game.current_index == 0:
                self.assertTrue(game.players[0].inked_this_turn
                                or not any(c.inkable for c in game.players[0].hand),
                                "AI skipped its ink drop")
            game.advance_turn()

    def test_ai_beats_random_convincingly(self):
        wins = 0
        games = 8
        for number in range(games):
            deck_a = DECKLISTS[number % 3]
            deck_b = DECKLISTS[(number + 1) % 3]
            game = Game([("AI", deck_a, SearchAI("AI")),
                         ("R", deck_b, RandomController("R", seed=number))],
                        seed=100 + number)
            wins += int(game.run() == 0)
        self.assertGreaterEqual(wins, games - 1)

    def test_ai_beats_the_heuristic_policy(self):
        wins = 0
        games = 12
        for number in range(games):
            deck_a = DECKLISTS[number % 3]
            deck_b = DECKLISTS[(number + 2) % 3]
            entries = [("AI", deck_a, SearchAI("AI")),
                       ("G", deck_b, GreedyAI("G"))]
            if number % 2:
                entries.reverse()
            game = Game(entries, seed=200 + number)
            winner = game.run()
            wins += int(game.players[winner].name == "AI")
        self.assertGreater(wins, games / 2, f"AI won only {wins}/{games}")

    def test_ai_can_pilot_every_deck(self):
        for deck in DECKLISTS:
            game = Game([("AI", deck, SearchAI("AI", beam_width=3, rollouts=2)),
                         ("R", RUBY_EMERALD, RandomController("R", seed=1))],
                        seed=11)
            self.assertIn(game.run(), (0, 1))


if __name__ == "__main__":
    unittest.main()
