"""Guards the claim that every card in the three starter decks is supported.

Every card must either have a dedicated behavioural test in ``test_cards.py`` or
be listed as vanilla there - and a card listed as vanilla must genuinely have no
abilities to implement.
"""

from __future__ import annotations

import unittest

import test_cards
from helpers import new_game

from lorcana import carddb as db
from lorcana.abilities import (ActivatedAbility, StaticAbility, TriggeredAbility)
from lorcana.actions import PlayAction
from lorcana.decks import DECKLISTS


def all_deck_cards():
    cards = {}
    for deck in DECKLISTS:
        for card in deck.cards:
            cards[card.id] = card
    return cards


class CoverageTests(unittest.TestCase):
    def test_every_deck_card_is_tested(self):
        vanilla = {card.id for card in test_cards.VANILLA}
        covered = test_cards.SPECIFIC | vanilla
        missing = sorted(set(all_deck_cards()) - covered)
        self.assertEqual(missing, [], f"cards with no test: {missing}")

    def test_vanilla_cards_really_have_no_abilities(self):
        for card in test_cards.VANILLA:
            self.assertEqual(card.abilities, (),
                             f"{card.full_name} has abilities and needs a real test")

    def test_no_card_is_in_both_lists(self):
        vanilla = {card.id for card in test_cards.VANILLA}
        self.assertEqual(vanilla & test_cards.SPECIFIC, set())

    def test_every_ability_is_a_known_kind(self):
        """A card whose text was never implemented would show up as an empty
        ability list on a card with rules text, so check that too."""
        known = (StaticAbility, TriggeredAbility, ActivatedAbility)
        for card in all_deck_cards().values():
            for ability in card.abilities:
                self.assertIsInstance(ability, known, card.full_name)
                if isinstance(ability, (TriggeredAbility, ActivatedAbility)):
                    self.assertIsNotNone(ability.effect,
                                         f"{card.full_name} has no effect")

    def test_cards_with_rules_text_have_an_implementation(self):
        keyword_only = {"Challenger", "Evasive", "Rush", "Ward", "Bodyguard",
                        "Support", "Reckless", "Singer", "Shift"}

        def is_keyword_only(text):
            stripped = text.replace("+", " ").replace(".", " ")
            words = [w for w in stripped.split() if not w.isdigit()]
            return all(word in keyword_only for word in words)

        for card in all_deck_cards().values():
            if not card.text or is_keyword_only(card.text):
                continue
            self.assertTrue(card.abilities,
                            f"{card.full_name} has rules text but no abilities: "
                            f"{card.text!r}")

    def test_decks_are_sixty_cards_and_legal_colours(self):
        for deck in DECKLISTS:
            self.assertEqual(len(deck.cards), 60, deck.name)
            self.assertEqual(len(deck.colors), 2, deck.name)
            counts = deck.counts()
            for card, count in counts.items():
                self.assertLessEqual(count, 4, f"{card.full_name} x{count}")

    def test_every_card_in_every_deck_can_actually_be_played(self):
        """Plays each card from hand with enough ink and a board to target."""
        for card in all_deck_cards().values():
            game = new_game(hand1=[card], ink1=10,
                            deck1=[db.OLAF] * 8, deck2=[db.GOONS] * 8)
            # Something on both sides so targeted effects have a legal target.
            from helpers import put_character, put_item
            put_character(game, 0, db.MICKEY_TRUE_FRIEND, damage=1)
            put_character(game, 1, db.MICKEY_STEAMBOAT, damage=1, ready=False)
            put_item(game, 1, db.DINGLEHOPPER)
            game.players[0].discard.append(db.SVEN)
            game.players[1].discard.append(db.GOONS)
            actions = [a for a in game.legal_actions()
                       if isinstance(a, PlayAction) and a.card is card]
            self.assertEqual(len(actions), 1, f"{card.full_name} is not playable")
            game.apply(actions[0])
            self.assertNotIn(card, game.players[0].hand, card.full_name)


if __name__ == "__main__":
    unittest.main()
