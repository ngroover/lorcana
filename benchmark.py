#!/usr/bin/python3
"""Play two players against each other and report a win rate.

Games are paired: every (deck pairing, shuffle seed) is played twice, once with
each side seated first, so the first-player advantage and the shuffle cancel out.
Without that pairing the noise swamps the differences you are trying to measure.

    ./benchmark.py --a ai --b greedy
    ./benchmark.py --a hard --b normal --seeds 10
    ./benchmark.py --a ai --b greedy --deck-a 1 --deck-b 3
"""

from __future__ import annotations

import argparse
import math
import statistics
import time

from lorcana.cli import make_controller
from lorcana.decks import DECKLISTS
from lorcana.game import Game

KINDS = ("ai", "easy", "normal", "hard", "greedy", "random")


def controller_for(kind, name, seed=None):
    if kind in ("easy", "normal", "hard"):
        return make_controller("ai", name, seed=seed, difficulty=kind)
    return make_controller(kind, name, seed=seed, difficulty="normal")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", default="ai", choices=KINDS)
    parser.add_argument("--b", default="greedy", choices=KINDS)
    parser.add_argument("--seeds", type=int, default=6,
                        help="shuffle seeds; each plays every pairing twice")
    parser.add_argument("--seed", type=int, default=1, help="first shuffle seed")
    parser.add_argument("--deck-a", type=int, help="restrict A to deck 1-3")
    parser.add_argument("--deck-b", type=int, help="restrict B to deck 1-3")
    parser.add_argument("--quiet", action="store_true", help="only the summary")
    args = parser.parse_args(argv)

    decks_a = [DECKLISTS[args.deck_a - 1]] if args.deck_a else DECKLISTS
    decks_b = [DECKLISTS[args.deck_b - 1]] if args.deck_b else DECKLISTS

    wins = played = 0
    turns = []
    start = time.time()
    for index in range(args.seeds):
        seed = args.seed + index * 977
        for deck_a in decks_a:
            for deck_b in decks_b:
                for a_first in (True, False):
                    entries = [("A", deck_a, controller_for(args.a, "A", seed)),
                               ("B", deck_b, controller_for(args.b, "B", seed + 7))]
                    if not a_first:
                        entries.reverse()
                    game = Game(entries, seed=seed, verbose=False)
                    winner = game.players[game.run()].name
                    wins += int(winner == "A")
                    played += 1
                    turns.append(game.turn_number)
                    if not args.quiet:
                        print(f"{winner} wins  "
                              f"[A:{deck_a.name.split('/')[0]} vs "
                              f"B:{deck_b.name.split('/')[0]}, "
                              f"{'A' if a_first else 'B'} first] "
                              f"{game.turn_number} turns")
    rate = wins / played
    stderr = math.sqrt(rate * (1 - rate) / played)
    elapsed = time.time() - start
    print()
    print(f"{args.a} vs {args.b}: {wins}/{played} = {100 * rate:.1f}% "
          f"+/- {100 * stderr:.1f}% for {args.a}")
    print(f"turns: median {statistics.median(turns):.0f}, "
          f"mean {statistics.mean(turns):.1f}")
    print(f"{elapsed:.0f}s total, {elapsed / played:.2f}s per game")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
