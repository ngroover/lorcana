"""Command line front end: play a game, or run bots against each other."""

from __future__ import annotations

import argparse
import sys
import time

from .ai import GreedyAI, SearchAI
from .controllers import HumanController, RandomController
from .decks import DECKLISTS, by_name
from .game import Game

PLAYER_KINDS = ("human", "ai", "greedy", "random")


def make_controller(kind, name, seed=None, difficulty="normal"):
    if kind == "human":
        return HumanController(name)
    if kind == "ai":
        presets = {
            # No lookahead at all: plays the position in front of it.
            "easy": dict(beam_width=2, max_depth=10, rollouts=1, samples=1,
                         reply_weight=0.0, follow_up=False),
            "normal": dict(beam_width=28, max_depth=20, rollouts=24, samples=4),
            "hard": dict(beam_width=64, max_depth=24, rollouts=48, samples=6),
        }
        return SearchAI(name, **presets.get(difficulty, presets["normal"]))
    if kind == "greedy":
        return GreedyAI(name)
    if kind == "random":
        return RandomController(name, seed=seed)
    raise ValueError(f"unknown player kind: {kind}")


def choose_deck_interactively(prompt):
    print(prompt)
    for index, deck in enumerate(DECKLISTS, 1):
        colors = "/".join(deck.colors)
        print(f"  {index}. {deck.name} [{colors}]")
    while True:
        raw = input(f"Deck [1-{len(DECKLISTS)}]: ").strip()
        deck = by_name(raw)
        if deck is not None:
            return deck
        print("Not a deck.")


def choose_kind_interactively(prompt):
    print(prompt)
    for index, kind in enumerate(PLAYER_KINDS, 1):
        print(f"  {index}. {kind}")
    while True:
        raw = input(f"Player type [1-{len(PLAYER_KINDS)}]: ").strip().lower()
        if raw.isdigit() and 1 <= int(raw) <= len(PLAYER_KINDS):
            return PLAYER_KINDS[int(raw) - 1]
        if raw in PLAYER_KINDS:
            return raw
        print("Not a player type.")


def build_game(args, seed=None, verbose=True):
    deck1 = by_name(args.deck1) if args.deck1 else None
    deck2 = by_name(args.deck2) if args.deck2 else None
    if deck1 is None:
        deck1 = choose_deck_interactively("Choose player 1's deck:")
    if deck2 is None:
        deck2 = choose_deck_interactively("Choose player 2's deck:")
    kind1 = args.p1 or choose_kind_interactively("Who plays player 1?")
    kind2 = args.p2 or choose_kind_interactively("Who plays player 2?")
    name1 = args.name1 or ("You" if kind1 == "human" else f"{kind1.title()} 1")
    name2 = args.name2 or ("You" if kind2 == "human" else f"{kind2.title()} 2")
    controllers = [
        make_controller(kind1, name1, seed=seed, difficulty=args.difficulty),
        make_controller(kind2, name2, seed=None if seed is None else seed + 1,
                        difficulty=args.difficulty),
    ]
    game = Game([(name1, deck1, controllers[0]), (name2, deck2, controllers[1])],
                seed=seed, verbose=verbose)
    return game, (kind1, kind2)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="play.py", description="Disney Lorcana simulator")
    parser.add_argument("--deck1", help="deck for player 1 (name or 1-3)")
    parser.add_argument("--deck2", help="deck for player 2 (name or 1-3)")
    parser.add_argument("--p1", choices=PLAYER_KINDS, help="player 1 type")
    parser.add_argument("--p2", choices=PLAYER_KINDS, help="player 2 type")
    parser.add_argument("--name1")
    parser.add_argument("--name2")
    parser.add_argument("--difficulty", choices=("easy", "normal", "hard"),
                        default="hard",
                        help="strength of the 'ai' player (default: hard)")
    parser.add_argument("--seed", type=int, help="random seed")
    parser.add_argument("--games", type=int, default=1,
                        help="play N games (bots only) and report the score")
    parser.add_argument("--quiet", action="store_true", help="suppress the game log")
    parser.add_argument("--list-decks", action="store_true")
    args = parser.parse_args(argv)

    if args.list_decks:
        for deck in DECKLISTS:
            print(deck.describe())
            print()
        return 0

    if args.games > 1:
        return run_series(args)

    game, _kinds = build_game(args, seed=args.seed, verbose=not args.quiet)
    winner = game.run()
    print()
    print(f"*** {game.players[winner].name} wins! "
          f"({game.players[0].name} {game.players[0].lore} lore - "
          f"{game.players[1].name} {game.players[1].lore} lore) ***")
    return 0


def run_series(args):
    wins = [0, 0]
    turns = []
    start = time.time()
    for number in range(args.games):
        seed = None if args.seed is None else args.seed + number * 1000
        game, kinds = build_game(args, seed=seed, verbose=False)
        if "human" in kinds:
            print("Refusing to run a series with a human player.", file=sys.stderr)
            return 1
        winner = game.run()
        wins[winner] += 1
        turns.append(game.turn_number)
        print(f"game {number + 1}: {game.players[winner].name} wins "
              f"({game.players[0].lore}-{game.players[1].lore}) "
              f"in {game.turn_number} turns")
    elapsed = time.time() - start
    total = sum(wins)
    print()
    print(f"{args.games} games in {elapsed:.1f}s "
          f"(avg {elapsed / max(1, total):.2f}s/game, "
          f"avg {sum(turns) / max(1, len(turns)):.1f} turns)")
    for index in (0, 1):
        print(f"player {index + 1}: {wins[index]} wins "
              f"({100.0 * wins[index] / max(1, total):.1f}%)")
    return 0
