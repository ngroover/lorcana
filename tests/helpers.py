"""Helpers for building small, fully controlled game states in tests."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lorcana import carddb as db                                    # noqa: E402
from lorcana.controllers import Controller, HeuristicController     # noqa: E402
from lorcana.decks import Decklist                                  # noqa: E402
from lorcana.game import Game                                       # noqa: E402
from lorcana.state import InkCard, InPlayCharacter, InPlayItem       # noqa: E402

FILLER = db.OLAF          # a vanilla 1-cost character used to pad decks/inkwells


class ScriptController(Controller):
    """Answers questions from a script, then falls back to a sane default.

    Each entry in ``answers`` may be an option, a predicate, an index, or a bool
    for confirmations.  ``choose_action`` is not used: tests drive the game by
    calling ``game.apply`` directly.
    """

    def __init__(self, name="test", answers=None, default_confirm=True):
        super().__init__(name)
        self.answers = list(answers or [])
        self.default_confirm = default_confirm
        self.asked = []

    def choose_action(self, game, player, actions):  # pragma: no cover
        raise AssertionError("tests should apply actions directly")

    def choose(self, game, player, prompt, options, kind, intent=None,
               optional=False, labeler=None, meta=None):
        self.asked.append((kind, intent, prompt))
        if self.answers:
            answer = self.answers.pop(0)
            if callable(answer) and not isinstance(answer, bool):
                for option in options:
                    if answer(option):
                        return option
                raise AssertionError(f"no option matched predicate for {prompt!r}")
            if isinstance(answer, int) and not isinstance(answer, bool) \
                    and answer < len(options) and answer not in options:
                return options[answer]
            if answer is None:
                return None
            return answer
        if kind == "confirm":
            return self.default_confirm if self.default_confirm in options \
                else options[0]
        return options[0]


def new_game(hand1=(), hand2=(), deck1=None, deck2=None, ink1=10, ink2=10,
             answers1=None, answers2=None, seed=1, turn_number=3, current=0):
    """A game positioned mid-turn, skipping set-up entirely."""
    controllers = [ScriptController("P1", answers1), ScriptController("P2", answers2)]
    decks = []
    for deck in (deck1, deck2):
        cards = list(deck) if deck is not None else [FILLER] * 20
        decks.append(Decklist("test", cards))
    game = Game([("P1", decks[0], controllers[0]),
                 ("P2", decks[1], controllers[1])], seed=seed)
    for index, (hand, ink) in enumerate(((hand1, ink1), (hand2, ink2))):
        player = game.players[index]
        player.deck = list(decks[index].cards)
        player.hand = list(hand)
        player.inkwell = [InkCard(FILLER, True) for _ in range(ink)]
    game.current_index = current
    game.turn_number = turn_number
    game.first_player_index = 0
    return game


def put_character(game, index, card, ready=True, drying=False, damage=0,
                  strength_mod=0):
    player = game.players[index]
    character = InPlayCharacter(card=card, uid=game.new_uid(), owner_index=index,
                                ready=ready, drying=drying, damage=damage,
                                strength_mod=strength_mod)
    player.characters.append(character)
    return character


def put_item(game, index, card, ready=True):
    player = game.players[index]
    item = InPlayItem(card=card, uid=game.new_uid(), owner_index=index, ready=ready)
    player.items.append(item)
    return item


def answers(game, index, *values):
    game.controllers[index].answers = list(values)


def named(card):
    """A predicate matching an in-play character or card by identity of card."""
    def predicate(option):
        return getattr(option, "card", option) is card
    return predicate


def heuristic_game(deck1, deck2, seed=1):
    game = Game([("A", deck1, HeuristicController("A")),
                 ("B", deck2, HeuristicController("B"))], seed=seed)
    return game
