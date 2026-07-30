#!/usr/bin/python3
"""Play bots against each other and report win rates.

    ./benchmark.py --a ai --b greedy --games 30
    ./benchmark.py --a ai --b greedy --games 30 --mirror   # every deck pairing
"""

from __future__ import annotations

import argparse
import statistics
import time

from lorcana.cli import make_controller
from lorcana.decks import DECKLISTS
from lorcana.game import Game

KINDS = ("ai", "greedy", "random", "easy", "hard")


def controller_for(kind, name, seed=None):
    if kind in ("easy", "hard"):
        return make_controller("ai", name, seed=seed, difficulty=kind)
    return make_controller(kind, name, seed=seed, difficulty="normal")


def play_match(kind_a, kind_b, deck_a, deck_b, seed, swap=False):
    """One game.  Returns (a_won, turns, seconds)."""
    controller_a = controller_for(kind_a, "A", seed=seed)
    controller_b = controller_for(kind_b, "B", seed=None if seed is None else seed + 7)
    entries = [("A", deck_a, controller_a), ("B", deck_b, controller_b)]
    if swap:
        entries.reverse()
    game = Game(entries, seed=seed, verbose=False)
    start = time.time()
    winner = game.run()
    elapsed = time.time() - start
    return game.players[winner].name == "A", game.turn_number, elapsed


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", default="ai", choices=KINDS)
    parser.add_argument("--b", default="greedy", choices=KINDS)
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--deck-a", type=int, default=None, help="1-3")
    parser.add_argument("--deck-b", type=int, default=None, help="1-3")
    parser.add_argument("--mirror", action="store_true",
                        help="rotate through all nine deck pairings")
    args = parser.parse_args(argv)

    pairings = []
    if args.mirror:
        for i in range(3):
            for j in range(3):
                pairings.append((DECKLISTS[i], DECKLISTS[j]))
    else:
        deck_a = DECKLISTS[(args.deck_a or 1) - 1]
        deck_b = DECKLISTS[(args.deck_b or 2) - 1]
        pairings.append((deck_a, deck_b))

    wins = 0
    played = 0
    turns = []
    times = []
    start = time.time()
    for number in range(args.games):
        deck_a, deck_b = pairings[number % len(pairings)]
        # Alternate who is seated first so the first-player advantage cancels.
        swap = bool(number % 2)
        won, turn_count, elapsed = play_match(args.a, args.b, deck_a, deck_b,
                                              args.seed + number * 101, swap=swap)
        wins += int(won)
        played += 1
        turns.append(turn_count)
        times.append(elapsed)
        print(f"game {number + 1:3d}: {'A' if won else 'B'} wins  "
              f"[{deck_a.name.split(' ')[0]} vs {deck_b.name.split(' ')[0]}"
              f"{', swapped' if swap else ''}] "
              f"{turn_count} turns, {elapsed:.2f}s")
    total = time.time() - start
    print()
    print(f"{args.a} vs {args.b}: {wins}/{played} = {100.0 * wins / played:.1f}% "
          f"win rate for {args.a}")
    print(f"turns: median {statistics.median(turns):.0f}, "
          f"mean {statistics.mean(turns):.1f}")
    print(f"time: {total:.1f}s total, {statistics.mean(times):.2f}s per game")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
