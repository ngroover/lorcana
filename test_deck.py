#!/usr/bin/python3

import unittest
from deck import Deck
from decklists import amber_amethyst,moana

class TestDeck(unittest.TestCase):
    def test_deck_create(self):
        d = Deck(amber_amethyst.cards)

    def test_deck_draw_probabilities(self):
        d = Deck(amber_amethyst.cards)
        probs = d.get_card_probabilities()

        # assert that we will draw moana with 1/60 probability
        self.assertTrue(moana in probs)
        self.assertEqual(probs[moana], 1/60)

if __name__ == '__main__':
    unittest.main()
