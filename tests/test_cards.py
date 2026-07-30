"""A test for every card in the three starter decks.

``test_coverage.py`` checks that this file covers all of them: any card carrying
an ability must appear in :data:`SPECIFIC`, and cards listed as vanilla must
really have no abilities.
"""

from __future__ import annotations

import unittest

from helpers import (answers, named, new_game, put_character, put_item)

from lorcana import carddb as db
from lorcana.actions import (ActivateAction, ChallengeAction, PlayAction,
                             QuestAction, ShiftAction)
from lorcana.cards import EVASIVE, RUSH, WARD

# Cards with a dedicated behavioural test below.
SPECIFIC = set()
# Cards whose whole rules text is stats plus plain keywords handled by the engine.
VANILLA = [
    # Amber / Amethyst
    db.OLAF, db.STITCH_NEW_DOG, db.MINNIE_MOUSE, db.MICKEY_TRUE_FRIEND,
    db.THE_WARDROBE, db.SVEN, db.DR_FACILIER_CHARLATAN, db.JAFAR_WICKED,
    db.RAFIKI,
    # Sapphire / Steel
    db.FLOUNDER, db.GOONS, db.AURORA_REGAL, db.PRINCE_ERIC, db.JASMINE_DISGUISED,
    db.KRISTOFF, db.MALEFICENT_SINISTER, db.MALEFICENT_UNINVITED, db.MUFASA,
    db.MAUI, db.HERCULES, db.CAPTAIN_HOOK_DUELIST,
    # Ruby / Emerald
    db.DUKE_OF_WESELTON, db.SERGEANT_TIBBS, db.DONALD_DUCK, db.HORACE,
    db.MICKEY_STEAMBOAT, db.PETER_PAN, db.PONGO, db.SCAR_FIERY_USURPER,
    db.THE_CAPTAIN, db.STITCH_ABOMINATION, db.ALADDIN_PRINCE_ALI,
]


def covers(*cards):
    """Register the cards a test method exercises."""
    def decorate(method):
        SPECIFIC.update(card.id for card in cards)
        return method
    return decorate


class VanillaCardTests(unittest.TestCase):
    def test_every_vanilla_card_can_be_played_and_keeps_its_stats(self):
        for card in VANILLA:
            game = new_game(hand1=[card], ink1=10, answers1=[False])
            game.apply(PlayAction(card))
            self.assertEqual(len(game.players[0].characters), 1, card.full_name)
            character = game.players[0].characters[0]
            self.assertIs(character.card, card)
            self.assertEqual(game.strength_of(character), card.strength)
            self.assertEqual(game.remaining_willpower(character), card.willpower)
            for keyword, value in card.keywords.items():
                self.assertEqual(game.keywords_of(character).get(keyword), value,
                                 f"{card.full_name} {keyword}")


class AmberAmethystTests(unittest.TestCase):
    @covers(db.PASCAL)
    def test_pascal_gains_evasive_with_another_character(self):
        game = new_game()
        pascal = put_character(game, 0, db.PASCAL)
        self.assertFalse(game.has_keyword(pascal, EVASIVE))
        put_character(game, 0, db.OLAF)
        self.assertTrue(game.has_keyword(pascal, EVASIVE))

    @covers(db.HEIHEI)
    def test_heihei_support_adds_its_strength_when_questing(self):
        game = new_game()
        heihei = put_character(game, 0, db.HEIHEI)        # 1/2 Support
        friend = put_character(game, 0, db.OLAF)
        answers(game, 0, named(db.OLAF))
        game.apply(QuestAction(heihei.uid))
        self.assertEqual(friend.strength_mod, 1)
        self.assertEqual(game.strength_of(friend), db.OLAF.strength + 1)

    @covers(db.DINGLEHOPPER)
    def test_dinglehopper_removes_one_damage(self):
        game = new_game()
        item = put_item(game, 0, db.DINGLEHOPPER)
        hurt = put_character(game, 0, db.OLAF, damage=2)
        answers(game, 0, named(db.OLAF))
        game.apply(ActivateAction(item.uid, 0, True))
        self.assertEqual(hurt.damage, 1)
        self.assertFalse(item.ready)

    @covers(db.CONTROL_YOUR_TEMPER)
    def test_control_your_temper_weakens_a_character(self):
        game = new_game(hand1=[db.CONTROL_YOUR_TEMPER], ink1=2)
        target = put_character(game, 1, db.SCAR_FIERY_USURPER)   # 5 strength
        answers(game, 0, named(db.SCAR_FIERY_USURPER))
        game.apply(PlayAction(db.CONTROL_YOUR_TEMPER))
        self.assertEqual(game.strength_of(target), 3)

    @covers(db.BE_OUR_GUEST)
    def test_be_our_guest_takes_a_character_from_the_top_four(self):
        game = new_game(hand1=[db.BE_OUR_GUEST], ink1=2,
                        deck1=[db.HAKUNA_MATATA, db.DINGLEHOPPER,
                               db.MICKEY_TRUE_FRIEND, db.CONTROL_YOUR_TEMPER,
                               db.OLAF])
        answers(game, 0, named(db.MICKEY_TRUE_FRIEND))
        game.apply(PlayAction(db.BE_OUR_GUEST))
        self.assertIn(db.MICKEY_TRUE_FRIEND, game.players[0].hand)
        self.assertEqual(game.players[0].deck[0], db.OLAF)     # 4 seen cards went under
        self.assertEqual(len(game.players[0].deck), 4)

    @covers(db.MAGIC_BROOM)
    def test_magic_broom_shuffles_a_card_from_a_discard_into_its_deck(self):
        game = new_game(hand1=[db.MAGIC_BROOM], ink1=3)
        game.players[0].discard.append(db.SVEN)
        answers(game, 0, True, lambda o: o[1] is db.SVEN)
        game.apply(PlayAction(db.MAGIC_BROOM))
        self.assertNotIn(db.SVEN, game.players[0].discard)
        self.assertIn(db.SVEN, game.players[0].deck)

    @covers(db.YZMA)
    def test_yzma_can_bottom_the_top_card_when_questing(self):
        game = new_game(deck1=[db.SVEN, db.OLAF, db.OLAF])
        yzma = put_character(game, 0, db.YZMA)
        answers(game, 0, False)          # put it on the bottom
        game.apply(QuestAction(yzma.uid))
        self.assertEqual(game.players[0].deck[0], db.OLAF)
        self.assertEqual(game.players[0].deck[-1], db.SVEN)

    @covers(db.FRIENDS_ON_THE_OTHER_SIDE)
    def test_friends_on_the_other_side_draws_two(self):
        game = new_game(hand1=[db.FRIENDS_ON_THE_OTHER_SIDE], ink1=3)
        game.apply(PlayAction(db.FRIENDS_ON_THE_OTHER_SIDE))
        self.assertEqual(len(game.players[0].hand), 2)

    @covers(db.MALEFICENT_SORCERESS)
    def test_maleficent_sorceress_may_draw(self):
        game = new_game(hand1=[db.MALEFICENT_SORCERESS], ink1=3, answers1=[True])
        game.apply(PlayAction(db.MALEFICENT_SORCERESS))
        self.assertEqual(len(game.players[0].hand), 1)
        game = new_game(hand1=[db.MALEFICENT_SORCERESS], ink1=3, answers1=[False])
        game.apply(PlayAction(db.MALEFICENT_SORCERESS))
        self.assertEqual(len(game.players[0].hand), 0)

    @covers(db.MAXIMUS)
    def test_maximus_weakens_a_character_on_play(self):
        game = new_game(hand1=[db.MAXIMUS], ink1=3)
        target = put_character(game, 1, db.HORACE)      # 4 strength
        answers(game, 0, named(db.HORACE))
        game.apply(PlayAction(db.MAXIMUS))
        self.assertEqual(game.strength_of(target), 2)

    @covers(db.PART_OF_YOUR_WORLD)
    def test_part_of_your_world_returns_a_character_from_the_discard(self):
        game = new_game(hand1=[db.PART_OF_YOUR_WORLD], ink1=3)
        game.players[0].discard.extend([db.SVEN, db.HAKUNA_MATATA])
        answers(game, 0, db.SVEN)
        game.apply(PlayAction(db.PART_OF_YOUR_WORLD))
        self.assertIn(db.SVEN, game.players[0].hand)
        self.assertNotIn(db.SVEN, game.players[0].discard)

    @covers(db.ARIEL_HUMAN_LEGS)
    def test_ariel_cannot_sing_songs(self):
        game = new_game(hand1=[db.FRIENDS_ON_THE_OTHER_SIDE], ink1=0)
        ariel = put_character(game, 0, db.ARIEL_HUMAN_LEGS)
        self.assertFalse(game.can_sing(ariel, db.FRIENDS_ON_THE_OTHER_SIDE))
        other = put_character(game, 0, db.MICKEY_TRUE_FRIEND)
        self.assertTrue(game.can_sing(other, db.FRIENDS_ON_THE_OTHER_SIDE))

    @covers(db.CINDERELLA_GENTLE)
    def test_cinderella_heals_a_princess_only(self):
        game = new_game()
        cinderella = put_character(game, 0, db.CINDERELLA_GENTLE)
        princess = put_character(game, 0, db.MINNIE_MOUSE, damage=3)
        put_character(game, 0, db.OLAF, damage=3)     # not a Princess
        answers(game, 0, named(db.MINNIE_MOUSE))
        game.apply(ActivateAction(cinderella.uid, 0, False))
        self.assertEqual(princess.damage, 0)
        self.assertFalse(cinderella.ready)

    @covers(db.HADES)
    def test_hades_returns_a_character_from_the_discard(self):
        game = new_game(hand1=[db.HADES], ink1=4)
        game.players[0].discard.append(db.SVEN)
        game.apply(PlayAction(db.HADES))
        self.assertIn(db.SVEN, game.players[0].hand)

    @covers(db.HAKUNA_MATATA)
    def test_hakuna_matata_heals_all_your_characters(self):
        game = new_game(hand1=[db.HAKUNA_MATATA], ink1=4)
        mine = put_character(game, 0, db.SVEN, damage=4)
        theirs = put_character(game, 1, db.MUFASA, damage=4)
        game.apply(PlayAction(db.HAKUNA_MATATA))
        self.assertEqual(mine.damage, 1)
        self.assertEqual(theirs.damage, 4)

    @covers(db.JETSAM)
    def test_jetsam_gives_flotsam_evasive(self):
        game = new_game()
        flotsam = put_character(game, 0, db.FLOTSAM)
        self.assertFalse(game.has_keyword(flotsam, EVASIVE))
        put_character(game, 0, db.JETSAM)
        self.assertTrue(game.has_keyword(flotsam, EVASIVE))

    @covers(db.FLOTSAM)
    def test_flotsam_gives_jetsam_rush(self):
        game = new_game()
        jetsam = put_character(game, 0, db.JETSAM)
        self.assertFalse(game.has_keyword(jetsam, RUSH))
        put_character(game, 0, db.FLOTSAM)
        self.assertTrue(game.has_keyword(jetsam, RUSH))

    @covers(db.MICKEY_WAYWARD_SORCERER)
    def test_wayward_sorcerer_discounts_brooms(self):
        game = new_game(hand1=[db.MAGIC_BROOM], ink1=1)
        self.assertEqual(game.effective_cost(game.players[0], db.MAGIC_BROOM), 2)
        put_character(game, 0, db.MICKEY_WAYWARD_SORCERER)
        self.assertEqual(game.effective_cost(game.players[0], db.MAGIC_BROOM), 1)
        answers(game, 0, False)
        game.apply(PlayAction(db.MAGIC_BROOM))
        self.assertEqual(game.players[0].available_ink, 0)

    @covers(db.MICKEY_WAYWARD_SORCERER)
    def test_wayward_sorcerer_recovers_a_banished_broom(self):
        game = new_game()
        put_character(game, 0, db.MICKEY_WAYWARD_SORCERER)
        broom = put_character(game, 0, db.MAGIC_BROOM)
        defender = put_character(game, 1, db.MUFASA, ready=False)   # 4/6
        answers(game, 0, True)
        game.apply(ChallengeAction(broom.uid, defender.uid))
        self.assertIn(db.MAGIC_BROOM, game.players[0].hand)
        self.assertNotIn(db.MAGIC_BROOM, game.players[0].discard)

    @covers(db.MOANA)
    def test_moana_readies_other_princesses_who_then_cannot_quest(self):
        game = new_game()
        moana = put_character(game, 0, db.MOANA)
        princess = put_character(game, 0, db.MINNIE_MOUSE, ready=False)
        plain = put_character(game, 0, db.OLAF, ready=False)
        answers(game, 0, True)
        game.apply(QuestAction(moana.uid))
        self.assertTrue(princess.ready)
        self.assertTrue(princess.cant_quest)
        self.assertFalse(plain.ready)
        self.assertEqual(game.players[0].lore, 3)

    @covers(db.DR_FACILIER_AGENT)
    def test_agent_provocateur_returns_a_banished_ally(self):
        game = new_game()
        put_character(game, 0, db.DR_FACILIER_AGENT)
        victim = put_character(game, 0, db.OLAF)
        defender = put_character(game, 1, db.MUFASA, ready=False)
        answers(game, 0, True)
        game.apply(ChallengeAction(victim.uid, defender.uid))
        self.assertIn(db.OLAF, game.players[0].hand)

    @covers(db.DR_FACILIER_AGENT)
    def test_agent_provocateur_can_shift_onto_the_charlatan(self):
        game = new_game(hand1=[db.DR_FACILIER_AGENT], ink1=5)
        put_character(game, 0, db.DR_FACILIER_CHARLATAN)
        shifts = [a for a in game.legal_actions() if isinstance(a, ShiftAction)]
        self.assertEqual(len(shifts), 1)
        game.apply(shifts[0])
        self.assertIs(game.players[0].characters[0].card, db.DR_FACILIER_AGENT)


class SapphireSteelTests(unittest.TestCase):
    @covers(db.DEVELOP_YOUR_BRAIN)
    def test_develop_your_brain_takes_one_of_two(self):
        game = new_game(hand1=[db.DEVELOP_YOUR_BRAIN], ink1=1,
                        deck1=[db.MAUI, db.GOONS, db.FLOUNDER])
        answers(game, 0, db.MAUI)
        game.apply(PlayAction(db.DEVELOP_YOUR_BRAIN))
        self.assertIn(db.MAUI, game.players[0].hand)
        self.assertEqual(game.players[0].deck[0], db.FLOUNDER)
        self.assertEqual(game.players[0].deck[-1], db.GOONS)

    @covers(db.FIRE_THE_CANNONS)
    def test_fire_the_cannons_deals_two_damage(self):
        game = new_game(hand1=[db.FIRE_THE_CANNONS], ink1=1)
        target = put_character(game, 1, db.MUFASA)
        answers(game, 0, named(db.MUFASA))
        game.apply(PlayAction(db.FIRE_THE_CANNONS))
        self.assertEqual(target.damage, 2)

    @covers(db.FIRE_THE_CANNONS)
    def test_damage_that_exceeds_willpower_banishes(self):
        game = new_game(hand1=[db.FIRE_THE_CANNONS], ink1=1)
        put_character(game, 1, db.GRAMMA_TALA)     # 1/1
        answers(game, 0, named(db.GRAMMA_TALA))
        answers(game, 1, False)      # decline her own inkwell trigger
        game.apply(PlayAction(db.FIRE_THE_CANNONS))
        self.assertEqual(game.players[1].characters, [])
        self.assertIn(db.GRAMMA_TALA, game.players[1].discard)

    @covers(db.MAGIC_GOLDEN_FLOWER)
    def test_magic_golden_flower_banishes_itself_to_heal_three(self):
        game = new_game()
        item = put_item(game, 0, db.MAGIC_GOLDEN_FLOWER)
        hurt = put_character(game, 0, db.MUFASA, damage=5)
        answers(game, 0, named(db.MUFASA))
        game.apply(ActivateAction(item.uid, 0, True))
        self.assertEqual(hurt.damage, 2)
        self.assertEqual(game.players[0].items, [])
        self.assertIn(db.MAGIC_GOLDEN_FLOWER, game.players[0].discard)

    @covers(db.COCONUT_BASKET)
    def test_coconut_basket_heals_when_you_play_a_character(self):
        game = new_game(hand1=[db.GOONS], ink1=2)
        put_item(game, 0, db.COCONUT_BASKET)
        hurt = put_character(game, 0, db.MUFASA, damage=3)
        answers(game, 0, True, named(db.MUFASA))
        game.apply(PlayAction(db.GOONS))
        self.assertEqual(hurt.damage, 1)

    @covers(db.FRYING_PAN)
    def test_frying_pan_stops_a_character_challenging_next_turn(self):
        game = new_game()
        item = put_item(game, 0, db.FRYING_PAN)
        target = put_character(game, 1, db.MAUI)
        answers(game, 0, named(db.MAUI))
        game.apply(ActivateAction(item.uid, 0, True))
        self.assertTrue(target.pending_flags.get("cant_challenge"))
        self.assertEqual(game.players[0].items, [])
        game.current_index = 1
        game.begin_turn()
        self.assertTrue(target.cant_challenge)
        put_character(game, 0, db.OLAF, ready=False)
        self.assertFalse(any(isinstance(a, ChallengeAction)
                             for a in game.legal_actions()))

    @covers(db.GRAMMA_TALA)
    def test_gramma_tala_goes_to_the_inkwell_when_banished(self):
        game = new_game()
        tala = put_character(game, 0, db.GRAMMA_TALA)
        answers(game, 0, True)
        game.banish_character(tala)
        self.assertNotIn(db.GRAMMA_TALA, game.players[0].discard)
        self.assertIn(db.GRAMMA_TALA, [ink.card for ink in game.players[0].inkwell])
        self.assertFalse(game.players[0].inkwell[-1].ready)

    @covers(db.ONE_JUMP_AHEAD)
    def test_one_jump_ahead_inks_the_top_card(self):
        game = new_game(hand1=[db.ONE_JUMP_AHEAD], ink1=2,
                        deck1=[db.MAUI, db.GOONS])
        game.apply(PlayAction(db.ONE_JUMP_AHEAD))
        self.assertEqual(game.players[0].total_ink, 3)
        self.assertIs(game.players[0].inkwell[-1].card, db.MAUI)
        self.assertFalse(game.players[0].inkwell[-1].ready)

    @covers(db.RANSACK)
    def test_ransack_draws_two_and_discards_two(self):
        game = new_game(hand1=[db.RANSACK], ink1=2,
                        deck1=[db.MAUI, db.GOONS, db.FLOUNDER])
        answers(game, 0, db.MAUI, db.GOONS)
        game.apply(PlayAction(db.RANSACK))
        self.assertEqual(game.players[0].hand, [])
        self.assertIn(db.MAUI, game.players[0].discard)
        self.assertIn(db.GOONS, game.players[0].discard)

    @covers(db.MICKEY_DETECTIVE)
    def test_detective_may_ink_the_top_card(self):
        game = new_game(hand1=[db.MICKEY_DETECTIVE], ink1=3,
                        deck1=[db.MAUI, db.GOONS])
        answers(game, 0, True)
        game.apply(PlayAction(db.MICKEY_DETECTIVE))
        self.assertEqual(game.players[0].total_ink, 4)
        self.assertIs(game.players[0].inkwell[-1].card, db.MAUI)

    @covers(db.SMASH)
    def test_smash_deals_three_damage(self):
        game = new_game(hand1=[db.SMASH], ink1=3)
        target = put_character(game, 1, db.MUFASA)
        answers(game, 0, named(db.MUFASA))
        game.apply(PlayAction(db.SMASH))
        self.assertEqual(target.damage, 3)

    @covers(db.AURORA_BRIAR_ROSE)
    def test_briar_rose_weakens_a_character(self):
        game = new_game(hand1=[db.AURORA_BRIAR_ROSE], ink1=4)
        target = put_character(game, 1, db.MAUI)
        answers(game, 0, named(db.MAUI))
        game.apply(PlayAction(db.AURORA_BRIAR_ROSE))
        self.assertEqual(game.strength_of(target), 6)

    @covers(db.AURORA_DREAMING_GUARDIAN)
    def test_dreaming_guardian_wards_your_other_characters(self):
        game = new_game()
        aurora = put_character(game, 0, db.AURORA_DREAMING_GUARDIAN)
        other = put_character(game, 0, db.GOONS)
        theirs = put_character(game, 1, db.GOONS)
        self.assertTrue(game.has_keyword(other, WARD))
        self.assertFalse(game.has_keyword(aurora, WARD))
        self.assertFalse(game.has_keyword(theirs, WARD))
        self.assertNotIn(other, game.targetable_characters(game.players[1]))

    @covers(db.BEAST_HARDHEADED)
    def test_beast_banishes_an_item(self):
        game = new_game(hand1=[db.BEAST_HARDHEADED], ink1=5)
        put_item(game, 1, db.DINGLEHOPPER)
        answers(game, 0, lambda o: o.card is db.DINGLEHOPPER)
        game.apply(PlayAction(db.BEAST_HARDHEADED))
        self.assertEqual(game.players[1].items, [])
        self.assertIn(db.DINGLEHOPPER, game.players[1].discard)

    @covers(db.GRAB_YOUR_SWORD)
    def test_grab_your_sword_hits_every_opposing_character(self):
        game = new_game(hand1=[db.GRAB_YOUR_SWORD], ink1=5)
        big = put_character(game, 1, db.MUFASA)
        small = put_character(game, 1, db.GRAMMA_TALA)
        mine = put_character(game, 0, db.GOONS)
        answers(game, 0, False)
        game.apply(PlayAction(db.GRAB_YOUR_SWORD))
        self.assertEqual(big.damage, 2)
        self.assertEqual(mine.damage, 0)
        self.assertNotIn(small, game.players[1].characters)

    @covers(db.SIMBA_RIGHTFUL_HEIR)
    def test_rightful_heir_gains_lore_when_it_banishes_in_a_challenge(self):
        game = new_game()
        simba = put_character(game, 0, db.SIMBA_RIGHTFUL_HEIR)     # 3/5
        defender = put_character(game, 1, db.GRAMMA_TALA, ready=False)
        answers(game, 1, False)
        game.apply(ChallengeAction(simba.uid, defender.uid))
        self.assertEqual(game.players[0].lore, 1)

    @covers(db.SIMBA_RIGHTFUL_HEIR)
    def test_rightful_heir_gains_nothing_on_the_opponents_turn(self):
        game = new_game(current=1)
        simba = put_character(game, 0, db.SIMBA_RIGHTFUL_HEIR, ready=False)
        attacker = put_character(game, 1, db.GRAMMA_TALA)
        game.apply(ChallengeAction(attacker.uid, simba.uid))
        self.assertEqual(game.players[0].lore, 0)

    @covers(db.SCAR_MASTERMIND)
    def test_mastermind_weakens_an_opposing_character_only(self):
        game = new_game(hand1=[db.SCAR_MASTERMIND], ink1=6)
        theirs = put_character(game, 1, db.MAUI)
        mine = put_character(game, 0, db.MAUI)
        answers(game, 0, named(db.MAUI))
        game.apply(PlayAction(db.SCAR_MASTERMIND))
        self.assertEqual(game.strength_of(theirs), 3)
        self.assertEqual(game.strength_of(mine), 8)

    @covers(db.SIMBA_RETURNED_KING)
    def test_returned_king_is_evasive_only_on_your_turn(self):
        game = new_game(current=0)
        simba = put_character(game, 0, db.SIMBA_RETURNED_KING)
        self.assertTrue(game.has_keyword(simba, EVASIVE))
        game.current_index = 1
        self.assertFalse(game.has_keyword(simba, EVASIVE))


class RubyEmeraldTests(unittest.TestCase):
    @covers(db.HES_GOT_A_SWORD)
    def test_hes_got_a_sword_buffs_strength(self):
        game = new_game(hand1=[db.HES_GOT_A_SWORD], ink1=1)
        mine = put_character(game, 0, db.SERGEANT_TIBBS)
        answers(game, 0, named(db.SERGEANT_TIBBS))
        game.apply(PlayAction(db.HES_GOT_A_SWORD))
        self.assertEqual(game.strength_of(mine), 4)
        game.end_turn()
        self.assertEqual(game.strength_of(mine), 2)

    @covers(db.SHIELD_OF_VIRTUE)
    def test_shield_of_virtue_readies_a_character_for_three_ink(self):
        game = new_game(ink1=3)
        item = put_item(game, 0, db.SHIELD_OF_VIRTUE)
        spent = put_character(game, 0, db.HORACE, ready=False)
        answers(game, 0, named(db.HORACE))
        game.apply(ActivateAction(item.uid, 0, True))
        self.assertTrue(spent.ready)
        self.assertTrue(spent.cant_quest)
        self.assertEqual(game.players[0].available_ink, 0)
        self.assertFalse(item.ready)

    @covers(db.SHIELD_OF_VIRTUE)
    def test_shield_of_virtue_needs_the_ink(self):
        game = new_game(ink1=2)
        item = put_item(game, 0, db.SHIELD_OF_VIRTUE)
        put_character(game, 0, db.HORACE, ready=False)
        self.assertFalse(any(isinstance(a, ActivateAction) and a.uid == item.uid
                             for a in game.legal_actions()))

    @covers(db.STAMPEDE)
    def test_stampede_only_hits_a_damaged_character(self):
        game = new_game(hand1=[db.STAMPEDE], ink1=1)
        healthy = put_character(game, 1, db.MUFASA)
        hurt = put_character(game, 1, db.THE_CAPTAIN, damage=1)
        answers(game, 0, named(db.THE_CAPTAIN))
        game.apply(PlayAction(db.STAMPEDE))
        self.assertEqual(hurt.damage, 3)
        self.assertEqual(healthy.damage, 0)

    @covers(db.VICIOUS_BETRAYAL)
    def test_vicious_betrayal_gives_villains_more(self):
        game = new_game(hand1=[db.VICIOUS_BETRAYAL, db.VICIOUS_BETRAYAL], ink1=2)
        villain = put_character(game, 0, db.SCAR_FIERY_USURPER)   # Villain, 5
        hero = put_character(game, 0, db.SERGEANT_TIBBS)          # not a Villain, 2
        answers(game, 0, named(db.SCAR_FIERY_USURPER), named(db.SERGEANT_TIBBS))
        game.apply(PlayAction(db.VICIOUS_BETRAYAL))
        game.apply(PlayAction(db.VICIOUS_BETRAYAL))
        self.assertEqual(game.strength_of(villain), 8)
        self.assertEqual(game.strength_of(hero), 4)

    @covers(db.CRUELLA_DE_VIL)
    def test_cruella_bounces_a_character_when_challenged_and_banished(self):
        game = new_game(current=1)
        cruella = put_character(game, 0, db.CRUELLA_DE_VIL, ready=False)  # 1/3
        attacker = put_character(game, 1, db.SCAR_FIERY_USURPER)          # 5/3
        answers(game, 0, True, named(db.SCAR_FIERY_USURPER))
        game.apply(ChallengeAction(attacker.uid, cruella.uid))
        self.assertNotIn(cruella, game.players[0].characters)
        self.assertNotIn(attacker, game.players[1].characters)
        self.assertIn(db.SCAR_FIERY_USURPER, game.players[1].hand)

    @covers(db.LEFOU)
    def test_lefou_readies_a_character_that_cannot_quest(self):
        game = new_game(hand1=[db.LEFOU], ink1=2)
        spent = put_character(game, 0, db.HORACE, ready=False)
        answers(game, 0, named(db.HORACE))
        game.apply(PlayAction(db.LEFOU))
        self.assertTrue(spent.ready)
        self.assertTrue(spent.cant_quest)

    @covers(db.MEGARA)
    def test_megara_buffs_on_play(self):
        game = new_game(hand1=[db.MEGARA], ink1=2)
        mine = put_character(game, 0, db.HORACE)
        answers(game, 0, named(db.HORACE))
        game.apply(PlayAction(db.MEGARA))
        self.assertEqual(game.strength_of(mine), 6)

    @covers(db.STOLEN_SCIMITAR)
    def test_stolen_scimitar_gives_aladdin_more(self):
        game = new_game()
        item = put_item(game, 0, db.STOLEN_SCIMITAR)
        aladdin = put_character(game, 0, db.ALADDIN_STREET_RAT)
        answers(game, 0, named(db.ALADDIN_STREET_RAT))
        game.apply(ActivateAction(item.uid, 0, True))
        self.assertEqual(game.strength_of(aladdin), db.ALADDIN_STREET_RAT.strength + 2)
        other = put_character(game, 0, db.HORACE)
        item.ready = True
        answers(game, 0, named(db.HORACE))
        game.apply(ActivateAction(item.uid, 0, True))
        self.assertEqual(game.strength_of(other), db.HORACE.strength + 1)

    @covers(db.ALADDIN_STREET_RAT)
    def test_street_rat_drains_a_lore(self):
        game = new_game(hand1=[db.ALADDIN_STREET_RAT], ink1=3)
        game.players[1].lore = 5
        game.apply(PlayAction(db.ALADDIN_STREET_RAT))
        self.assertEqual(game.players[1].lore, 4)

    @covers(db.IAGO)
    def test_iago_makes_a_character_reckless_next_turn(self):
        game = new_game()
        iago = put_character(game, 0, db.IAGO)
        target = put_character(game, 1, db.MICKEY_STEAMBOAT)
        answers(game, 0, named(db.MICKEY_STEAMBOAT))
        game.apply(ActivateAction(iago.uid, 0, False))
        self.assertTrue(target.pending_flags.get("reckless"))
        game.current_index = 1
        game.begin_turn()
        self.assertTrue(game.has_keyword(target, "Reckless"))
        self.assertFalse(any(isinstance(a, QuestAction)
                             for a in game.legal_actions()))

    @covers(db.JASPER)
    def test_jasper_stops_an_opposing_character_questing(self):
        game = new_game()
        jasper = put_character(game, 0, db.JASPER)
        target = put_character(game, 1, db.MICKEY_STEAMBOAT)
        answers(game, 0, named(db.MICKEY_STEAMBOAT))
        game.apply(QuestAction(jasper.uid))
        self.assertTrue(target.pending_flags.get("cant_quest"))
        game.current_index = 1
        game.begin_turn()
        self.assertTrue(target.cant_quest)
        self.assertFalse(any(isinstance(a, QuestAction)
                             for a in game.legal_actions()))

    @covers(db.MOTHER_KNOWS_BEST)
    def test_mother_knows_best_returns_a_character_to_hand(self):
        game = new_game(hand1=[db.MOTHER_KNOWS_BEST], ink1=3)
        target = put_character(game, 1, db.MAUI, damage=3)
        answers(game, 0, named(db.MAUI))
        game.apply(PlayAction(db.MOTHER_KNOWS_BEST))
        self.assertEqual(game.players[1].characters, [])
        self.assertIn(db.MAUI, game.players[1].hand)

    @covers(db.DRAGON_FIRE)
    def test_dragon_fire_banishes_outright(self):
        game = new_game(hand1=[db.DRAGON_FIRE], ink1=5)
        put_character(game, 1, db.MAUI)
        answers(game, 0, named(db.MAUI))
        game.apply(PlayAction(db.DRAGON_FIRE))
        self.assertEqual(game.players[1].characters, [])
        self.assertIn(db.MAUI, game.players[1].discard)

    @covers(db.MAD_HATTER)
    def test_mad_hatter_draws_when_challenged(self):
        game = new_game(current=1)
        hatter = put_character(game, 0, db.MAD_HATTER, ready=False)
        attacker = put_character(game, 1, db.SERGEANT_TIBBS)
        answers(game, 0, True)
        game.apply(ChallengeAction(attacker.uid, hatter.uid))
        self.assertEqual(len(game.players[0].hand), 1)

    @covers(db.STEAL_FROM_THE_RICH)
    def test_steal_from_the_rich_drains_on_every_quest_this_turn(self):
        game = new_game(hand1=[db.STEAL_FROM_THE_RICH], ink1=5)
        game.players[1].lore = 6
        first = put_character(game, 0, db.HORACE)
        second = put_character(game, 0, db.SERGEANT_TIBBS)
        game.apply(PlayAction(db.STEAL_FROM_THE_RICH))
        game.apply(QuestAction(first.uid))
        game.apply(QuestAction(second.uid))
        self.assertEqual(game.players[1].lore, 4)
        game.end_turn()
        self.assertEqual(game.players[0].quest_drain, 0)

    @covers(db.RAPUNZEL_LETTING_DOWN)
    def test_rapunzel_drains_a_lore(self):
        game = new_game(hand1=[db.RAPUNZEL_LETTING_DOWN], ink1=6)
        game.players[1].lore = 3
        game.apply(PlayAction(db.RAPUNZEL_LETTING_DOWN))
        self.assertEqual(game.players[1].lore, 2)

    @covers(db.ALADDIN_HEROIC_OUTLAW)
    def test_heroic_outlaw_swings_four_lore_on_a_banish(self):
        game = new_game()
        game.players[1].lore = 5
        aladdin = put_character(game, 0, db.ALADDIN_HEROIC_OUTLAW)   # 5/5
        defender = put_character(game, 1, db.SERGEANT_TIBBS, ready=False)
        game.apply(ChallengeAction(aladdin.uid, defender.uid))
        self.assertEqual(game.players[0].lore, 2)
        self.assertEqual(game.players[1].lore, 3)

    @covers(db.ALADDIN_HEROIC_OUTLAW)
    def test_heroic_outlaw_shifts_onto_another_aladdin(self):
        game = new_game(hand1=[db.ALADDIN_HEROIC_OUTLAW], ink1=5)
        put_character(game, 0, db.ALADDIN_STREET_RAT)
        shifts = [a for a in game.legal_actions() if isinstance(a, ShiftAction)]
        self.assertEqual(len(shifts), 1)
        game.apply(shifts[0])
        self.assertIs(game.players[0].characters[0].card, db.ALADDIN_HEROIC_OUTLAW)


if __name__ == "__main__":
    unittest.main()
