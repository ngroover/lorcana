#!/usr/bin/python3

import unittest
from deck import Deck
from decklists import amber_amethyst,moana

class TestDeck(unittest.TestCase):
    def test_deck_create(self):
        d = Deck(amber_amethyst.cards)

    def test_deck_draw_probabilities(self):
        d = Deck(amber_amethyst.cards)
        choices = d.get_card_choices()

        self.assertEqual(60, d.get_total_cards())
        self.assertTrue(moana in choices)
        # moana has a weight of 1 here since there's only 1 in the deck
        # probability is 1/60
        self.assertEqual(choices[moana], 1)

if __name__ == '__main__':
    unittest.main()
