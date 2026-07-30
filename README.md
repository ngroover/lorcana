# Lorcana simulator

A Disney Lorcana (*The First Chapter*) engine, a command line client, and a
search-based AI opponent.  All three First Chapter starter decks are implemented
card for card — every printed ability, not just stats.

```
./play.py                       # pick decks and players interactively
./play.py --deck1 1 --deck2 3 --p1 human --p2 ai
./play.py --list-decks          # show the three decklists
./benchmark.py --a ai --b greedy --games 50 --mirror
```

## Playing

`play.py` prompts for each side's deck and player type (`human`, `ai`, `greedy`,
`random`), or takes them as flags.  On your turn it prints the board, your hand
and a numbered list of every legal action; type the number.  Choices that come up
while a card resolves ("which character takes the damage?") are prompted the same
way, with `0` to decline anything optional.

`--difficulty easy|normal|hard` sets how hard the `ai` player thinks.  A normal
AI turn takes a fraction of a second.

## The three decks

| Deck | Colours | Plan |
| --- | --- | --- |
| Amber/Amethyst | amber, amethyst | Wide boards, healing, song support |
| Sapphire/Steel | sapphire, steel | Ramp, removal, big finishers |
| Ruby/Emerald | ruby, emerald | Tempo, lore drain, hard removal |

Each is the printed 60-card starter deck; 86 distinct cards in total.

## Rules implemented

Ink drops (one per turn, usable immediately), the drying rule, questing,
challenging with simultaneous damage, banishment and the discard, singing songs
for free, shifting onto a character with the same name, alter-hand at the start
of the game, the first player skipping their first draw, winning at 20 lore, and
losing if you cannot draw.

Keywords: **Evasive**, **Rush**, **Ward**, **Bodyguard**, **Support**,
**Reckless**, **Challenger +N**, **Singer N**, **Shift N**.

Card abilities come in three shapes (`lorcana/abilities.py`): static abilities
that are queried live (Pascal's conditional Evasive, Aurora granting Ward, the
Broom discount), triggered abilities on game events (on play, on quest, when
challenged, when banished, when this banishes another character in a challenge,
whenever you play a character), and activated abilities with a cost (exert,
banish this item, pay ink).

### Simplifications

* Be Our Guest leaves the cards you did not take on the bottom in the order they
  were seen, rather than asking you to order them.
* Simultaneous triggers resolve in a fixed order instead of asking you to choose.

## The AI

`lorcana/ai.py`.  The AI plans a whole turn at a time:

1. Clone the game and re-randomise what it cannot see — the opponent's hand and
   both deck orders — so it never plays against knowledge it should not have.
2. Beam-search sequences of main-phase actions, ranking partial plans with the
   static evaluation in `lorcana/evaluate.py`.  Duplicate positions reached by
   different action orders are collapsed.
3. Take the most promising complete plans and simulate the opponent's reply turn
   against several guesses at their hand, plus its own follow-up turn.  This is
   what keeps it from questing into a lethal counter-attack or over-extending.
4. Play that plan, replanning if the game diverges from what it simulated.

Its opponent model — and its answer to the small questions inside card effects —
is the rule-based policy in `lorcana/controllers.py`, which is also available as
the `greedy` player.

Measured over 100+ games across all nine deck pairings, alternating who goes
first: the AI beats `random` ~100% of the time and the `greedy` policy ~90%.
Evaluation weights live in `Weights` in `lorcana/evaluate.py`; `benchmark.py`
plays configurations off against each other.

## Tests

```
python3 -m unittest discover -s tests -t tests
```

115 tests: the rules, a behavioural test for every card that has an ability, and
a coverage guard that fails if a card in any deck has rules text but no
implementation, or is listed as vanilla while carrying abilities.

## Layout

| File | What it holds |
| --- | --- |
| `lorcana/cards.py` | Immutable card model and keyword names |
| `lorcana/carddb.py` | All 86 cards with their abilities |
| `lorcana/decks.py` | The three 60-card starter decks |
| `lorcana/abilities.py` | Static / triggered / activated ability shapes |
| `lorcana/effects.py` | What abilities actually do |
| `lorcana/statics.py` | The always-on abilities |
| `lorcana/state.py` | Mutable player and in-play state |
| `lorcana/actions.py` | Main-phase actions |
| `lorcana/game.py` | The rules engine |
| `lorcana/controllers.py` | Random, heuristic and human players |
| `lorcana/evaluate.py` | Position evaluation and its weights |
| `lorcana/ai.py` | The search AI |
| `lorcana/cli.py` | Command line front end |
