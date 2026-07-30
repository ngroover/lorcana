# Lorcana simulator

A Disney Lorcana (*The First Chapter*) engine, a command line client, and a
search-based AI opponent.  All three First Chapter starter decks are implemented
card for card — every printed ability, not just stats.

```
./play.py                       # pick decks and players interactively
./play.py --deck1 1 --deck2 3 --p1 human --p2 ai
./play.py --list-decks          # show the three decklists
./benchmark.py --a ai --b greedy   # bots only: measure a win rate
```

## Playing

`play.py` prompts for each side's deck and player type (`human`, `ai`, `greedy`,
`random`), or takes them as flags.  On your turn it prints the board, your hand
and a numbered list of every legal action; type the number.  Choices that come up
while a card resolves ("which character takes the damage?") are prompted the same
way, with `0` to decline anything optional.

`--difficulty easy|normal|hard` sets how hard the `ai` player thinks; it defaults
to `hard`, which still takes only about a third of a second per turn.

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

`easy` turns the lookahead off entirely, if you want a gentler game.

### How strong is it?

Measured with `benchmark.py`, which pairs games: every deck pairing and shuffle
is played twice, once with each side going first, so the first-player advantage
and the shuffle cancel out. Without that pairing the run-to-run noise (±4%)
swamps the differences you are trying to measure — an identical-configuration
control run reads exactly 50.0%.

| Matchup | Result |
| --- | --- |
| AI vs `greedy` | 91.7% ± 2.7% (108 paired games) |
| AI vs `random` | 100% (72 games) |
| `normal` vs `easy` | 70.8% ± 5.4% (72 games) |

Against a human it plays a coherent game: it inks every turn, holds a quester
back rather than losing it to a challenge, aims removal at what it cannot
otherwise answer, and sets up damage-then-challenge kills. It is not unbeatable
— playing it myself, a line built around re-readying a protected 3-lore quester
with Shield of Virtue got there — so if you are winning comfortably, that is a
real result and not a rigged benchmark.

Evaluation weights live in `Weights` in `lorcana/evaluate.py`, all tuned by
paired self-play. Two findings worth knowing if you tune further: valuing lore
mostly through a *quadratic* term (early lore matters less than board presence,
late lore decides the game) beat a large linear weight, and a steeply
diminishing inkwell curve is what makes "ink every turn, then stop around seven"
fall out of the evaluation rather than being hard-coded. Self-play cannot see a
mistake both sides share, so weights that measure neutral there were kept only
when they were also independently justified.

## Tests

```
python3 -m unittest discover -s tests -t tests
```

118 tests: the rules, a behavioural test for every card that has an ability, and
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
