"""Core rules: turn structure, ink, questing, challenging, keywords, songs, shift."""

from __future__ import annotations

import unittest

from helpers import new_game, put_character, put_item

from lorcana import carddb as db
from lorcana.actions import (ChallengeAction, InkAction, PassAction,
                             PlayAction, QuestAction, ShiftAction, SingAction)
from lorcana.cards import RECKLESS
from lorcana.decks import DECKLISTS
from lorcana.game import Game
from lorcana.controllers import HeuristicController


class InkTests(unittest.TestCase):
    def test_ink_once_per_turn(self):
        game = new_game(hand1=[db.OLAF, db.STITCH_NEW_DOG], ink1=0)
        actions = game.legal_actions()
        self.assertTrue(any(isinstance(a, InkAction) for a in actions))
        game.apply(InkAction(db.OLAF))
        self.assertEqual(game.players[0].total_ink, 1)
        self.assertEqual(game.players[0].available_ink, 1)  # usable immediately
        self.assertFalse(any(isinstance(a, InkAction) for a in game.legal_actions()))

    def test_uninkable_cards_cannot_be_inked(self):
        game = new_game(hand1=[db.RAFIKI], ink1=0)   # Rafiki is not inkable
        self.assertFalse(any(isinstance(a, InkAction) for a in game.legal_actions()))

    def test_playing_a_card_exerts_ink(self):
        game = new_game(hand1=[db.MOANA], ink1=6)
        game.apply(PlayAction(db.MOANA))
        self.assertEqual(game.players[0].available_ink, 1)
        self.assertEqual(game.players[0].total_ink, 6)

    def test_cannot_play_without_ink(self):
        game = new_game(hand1=[db.MOANA], ink1=4)
        self.assertFalse(any(isinstance(a, PlayAction) and a.card is db.MOANA
                             for a in game.legal_actions()))


class DryingTests(unittest.TestCase):
    def test_freshly_played_character_cannot_quest_or_challenge(self):
        game = new_game(hand1=[db.STITCH_NEW_DOG], ink1=5)
        put_character(game, 1, db.OLAF, ready=False)
        game.apply(PlayAction(db.STITCH_NEW_DOG))
        character = game.players[0].characters[0]
        self.assertTrue(character.drying)
        self.assertFalse(any(isinstance(a, (QuestAction, ChallengeAction))
                             for a in game.legal_actions()))

    def test_rush_allows_challenging_the_turn_it_is_played(self):
        game = new_game(hand1=[db.RAFIKI], ink1=5)
        put_character(game, 1, db.OLAF, ready=False)
        game.apply(PlayAction(db.RAFIKI))
        actions = game.legal_actions()
        self.assertTrue(any(isinstance(a, ChallengeAction) for a in actions))
        self.assertFalse(any(isinstance(a, QuestAction) for a in actions))

    def test_characters_dry_at_the_start_of_your_next_turn(self):
        game = new_game()
        character = put_character(game, 0, db.OLAF, drying=True, ready=False)
        game.begin_turn()
        self.assertFalse(character.drying)
        self.assertTrue(character.ready)


class QuestTests(unittest.TestCase):
    def test_questing_gains_lore_and_exerts(self):
        game = new_game()
        character = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        game.apply(QuestAction(character.uid))
        self.assertEqual(game.players[0].lore, 2)
        self.assertFalse(character.ready)

    def test_twenty_lore_wins(self):
        game = new_game()
        game.players[0].lore = 19
        character = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        game.apply(QuestAction(character.uid))
        self.assertEqual(game.winner, 0)


class ChallengeTests(unittest.TestCase):
    def test_can_only_challenge_exerted_characters(self):
        game = new_game()
        put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        put_character(game, 1, db.OLAF, ready=True)
        self.assertFalse(any(isinstance(a, ChallengeAction)
                             for a in game.legal_actions()))
        game.players[1].characters[0].ready = False
        self.assertTrue(any(isinstance(a, ChallengeAction)
                            for a in game.legal_actions()))

    def test_challenge_deals_damage_both_ways(self):
        game = new_game()
        attacker = put_character(game, 0, db.MICKEY_TRUE_FRIEND)   # 3/3
        defender = put_character(game, 1, db.THE_WARDROBE, ready=False)  # 3/4
        game.apply(ChallengeAction(attacker.uid, defender.uid))
        self.assertEqual(defender.damage, 3)
        self.assertEqual(attacker.damage, 3)
        self.assertNotIn(attacker, game.players[0].characters)
        self.assertIn(db.MICKEY_TRUE_FRIEND, game.players[0].discard)
        self.assertIn(defender, game.players[1].characters)

    def test_challenger_keyword_adds_strength_only_when_challenging(self):
        game = new_game()
        attacker = put_character(game, 0, db.DR_FACILIER_CHARLATAN)  # 0/4 Challenger +2
        defender = put_character(game, 1, db.OLAF, ready=False)      # 1/3
        self.assertEqual(game.strength_of(attacker), 0)
        self.assertEqual(game.strength_of(attacker, challenging=True), 2)
        game.apply(ChallengeAction(attacker.uid, defender.uid))
        self.assertEqual(defender.damage, 2)

    def test_evasive_can_only_be_challenged_by_evasive(self):
        game = new_game()
        plain = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        put_character(game, 1, db.PETER_PAN, ready=False)  # Evasive
        self.assertEqual(game.challenge_targets(plain), [])
        evasive = put_character(game, 0, db.PONGO)         # Evasive
        self.assertEqual(len(game.challenge_targets(evasive)), 1)

    def test_bodyguard_must_be_challenged_first(self):
        game = new_game()
        attacker = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        put_character(game, 1, db.OLAF, ready=False)
        guard = put_character(game, 1, db.HERCULES, ready=False)   # Bodyguard
        targets = game.challenge_targets(attacker)
        self.assertEqual([t.card for t in targets], [db.HERCULES])
        self.assertIs(targets[0], guard)

    def test_bodyguard_may_enter_play_exerted(self):
        game = new_game(hand1=[db.HERCULES], ink1=5, answers1=[True])
        game.apply(PlayAction(db.HERCULES))
        self.assertFalse(game.players[0].characters[0].ready)

    def test_ward_blocks_targeting_but_not_challenges(self):
        game = new_game(hand1=[db.FIRE_THE_CANNONS], ink1=5)
        warded = put_character(game, 1, db.ALADDIN_PRINCE_ALI, ready=False)
        attacker = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        self.assertNotIn(warded, game.targetable_characters(game.players[0]))
        self.assertIn(warded, game.challenge_targets(attacker))

    def test_reckless_must_challenge_and_cannot_quest(self):
        game = new_game()
        character = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        character.extra_keywords[RECKLESS] = True
        put_character(game, 1, db.OLAF, ready=False)
        actions = game.legal_actions()
        self.assertFalse(any(isinstance(a, QuestAction) for a in actions))
        self.assertFalse(any(isinstance(a, PassAction) for a in actions))
        self.assertTrue(any(isinstance(a, ChallengeAction) for a in actions))


class SongTests(unittest.TestCase):
    def test_singer_cost_lets_a_cheap_character_sing(self):
        game = new_game(hand1=[db.GRAB_YOUR_SWORD], ink1=0)   # 5-cost song
        singer = put_character(game, 0, db.CINDERELLA_GENTLE)  # cost 4, Singer 5
        self.assertTrue(game.can_sing(singer, db.GRAB_YOUR_SWORD))
        actions = game.legal_actions()
        self.assertTrue(any(isinstance(a, SingAction) for a in actions))

    def test_cost_of_character_must_cover_the_song(self):
        game = new_game(hand1=[db.GRAB_YOUR_SWORD], ink1=0)
        weak = put_character(game, 0, db.OLAF)     # cost 1
        self.assertFalse(game.can_sing(weak, db.GRAB_YOUR_SWORD))

    def test_singing_exerts_the_singer_and_is_free(self):
        game = new_game(hand1=[db.FRIENDS_ON_THE_OTHER_SIDE], ink1=0)
        singer = put_character(game, 0, db.MICKEY_TRUE_FRIEND)   # cost 3
        game.apply(SingAction(db.FRIENDS_ON_THE_OTHER_SIDE, singer.uid))
        self.assertFalse(singer.ready)
        self.assertEqual(len(game.players[0].hand), 2)   # drew 2
        self.assertIn(db.FRIENDS_ON_THE_OTHER_SIDE, game.players[0].discard)

    def test_drying_character_cannot_sing(self):
        game = new_game(hand1=[db.FRIENDS_ON_THE_OTHER_SIDE], ink1=0)
        singer = put_character(game, 0, db.MICKEY_TRUE_FRIEND, drying=True)
        self.assertFalse(game.can_sing(singer, db.FRIENDS_ON_THE_OTHER_SIDE))


class ShiftTests(unittest.TestCase):
    def test_shift_pays_the_shift_cost_and_keeps_state(self):
        game = new_game(hand1=[db.AURORA_DREAMING_GUARDIAN], ink1=4)
        base = put_character(game, 0, db.AURORA_REGAL, damage=1)
        actions = game.legal_actions()
        shifts = [a for a in actions if isinstance(a, ShiftAction)]
        self.assertEqual(len(shifts), 1)
        game.apply(shifts[0])
        self.assertEqual(game.players[0].available_ink, 1)     # Shift 3 of 4 ink
        self.assertIs(base.card, db.AURORA_DREAMING_GUARDIAN)
        self.assertEqual(base.damage, 1)
        self.assertEqual(base.underneath, [db.AURORA_REGAL])
        self.assertEqual(len(game.players[0].characters), 1)

    def test_shift_needs_a_matching_name(self):
        game = new_game(hand1=[db.AURORA_DREAMING_GUARDIAN], ink1=4)
        put_character(game, 0, db.OLAF)
        self.assertFalse(any(isinstance(a, ShiftAction) for a in game.legal_actions()))

    def test_banishing_a_shifted_character_discards_the_whole_stack(self):
        game = new_game(hand1=[db.AURORA_DREAMING_GUARDIAN], ink1=4)
        put_character(game, 0, db.AURORA_REGAL)
        game.apply([a for a in game.legal_actions() if isinstance(a, ShiftAction)][0])
        character = game.players[0].characters[0]
        game.banish_character(character)
        self.assertIn(db.AURORA_DREAMING_GUARDIAN, game.players[0].discard)
        self.assertIn(db.AURORA_REGAL, game.players[0].discard)


class TurnStructureTests(unittest.TestCase):
    def test_first_player_skips_the_first_draw(self):
        game = new_game(turn_number=1, current=0)
        game.first_player_index = 0
        before = len(game.players[0].hand)
        game.begin_turn()
        self.assertEqual(len(game.players[0].hand), before)
        game.advance_turn()
        before2 = len(game.players[1].hand)
        game.begin_turn()
        self.assertEqual(len(game.players[1].hand), before2 + 1)

    def test_empty_deck_at_draw_step_loses(self):
        game = new_game(turn_number=5, current=0)
        game.players[0].deck = []
        game.begin_turn()
        self.assertEqual(game.winner, 1)
        self.assertTrue(game.players[0].lost_to_empty_deck)

    def test_end_of_turn_clears_temporary_effects(self):
        game = new_game()
        character = put_character(game, 0, db.OLAF, strength_mod=3)
        character.cant_quest = True
        character.extra_keywords[RECKLESS] = True
        game.end_turn()
        self.assertEqual(character.strength_mod, 0)
        self.assertFalse(character.cant_quest)
        self.assertEqual(character.extra_keywords, {})

    def test_pending_flags_apply_at_the_start_of_the_owners_turn(self):
        game = new_game()
        character = put_character(game, 0, db.OLAF)
        character.pending_flags["cant_quest"] = True
        game.begin_turn()
        self.assertTrue(character.cant_quest)
        self.assertEqual(character.pending_flags, {})

    def test_ink_and_characters_ready_at_the_start_of_the_turn(self):
        game = new_game(ink1=3)
        for ink in game.players[0].inkwell:
            ink.ready = False
        character = put_character(game, 0, db.OLAF, ready=False)
        item = put_item(game, 0, db.DINGLEHOPPER, ready=False)
        game.begin_turn()
        self.assertEqual(game.players[0].available_ink, 3)
        self.assertTrue(character.ready)
        self.assertTrue(item.ready)


class FullGameTests(unittest.TestCase):
    def test_heuristic_players_finish_every_deck_pairing(self):
        for first in range(3):
            for second in range(3):
                game = Game([("A", DECKLISTS[first], HeuristicController("A")),
                             ("B", DECKLISTS[second], HeuristicController("B"))],
                            seed=first * 10 + second)
                winner = game.run()
                self.assertIn(winner, (0, 1))
                self.assertTrue(game.players[winner].lore >= 20
                                or game.players[1 - winner].lost_to_empty_deck
                                or game.turn_number > 100)

    def test_cloning_does_not_affect_the_original(self):
        game = new_game(hand1=[db.MOANA], ink1=6)
        clone = game.fast_clone()
        clone.apply(PlayAction(db.MOANA))
        self.assertEqual(len(game.players[0].hand), 1)
        self.assertEqual(len(game.players[0].characters), 0)
        self.assertEqual(len(clone.players[0].characters), 1)

    def test_clone_for_search_hides_the_opponent_hand(self):
        game = new_game(hand1=[db.MOANA], hand2=[db.MAUI, db.MUFASA])
        game.players[1].deck = [db.GOONS] * 20
        clone = game.clone_for_search(0)
        self.assertEqual(len(clone.players[1].hand), 2)
        self.assertEqual(clone.players[0].hand, [db.MOANA])
        pool = set(game.players[1].hand) | set(game.players[1].deck)
        for card in clone.players[1].hand:
            self.assertIn(card, pool)


if __name__ == "__main__":
    unittest.main()
