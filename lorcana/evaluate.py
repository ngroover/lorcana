"""Static evaluation of a game state, shared by the heuristic policy and the AI.

All the tunable numbers live in :class:`Weights` so that two configurations can
be played off against each other (see ``benchmark.py``).
"""

from __future__ import annotations

from dataclasses import dataclass

from .cards import (BODYGUARD, CHALLENGER, EVASIVE, RECKLESS, RUSH, SUPPORT,
                    WARD)

WIN_SCORE = 1_000_000.0


@dataclass(frozen=True)
class Weights:
    # Lore: the win condition, worth more the closer you are to 20.  The linear
    # term is deliberately modest and the quadratic term does the work: early
    # lore matters less than board presence, late lore decides the game.
    lore: float = 1.2
    lore_curve: float = 0.05
    # A character in play.
    character_base: float = 1.0
    character_cost: float = 0.35     # ink invested: a big body is harder to replace
    character_lore: float = 1.6      # a quester keeps paying out every turn
    character_strength: float = 0.40
    character_willpower: float = 0.45
    evasive: float = 0.9
    ward: float = 0.6
    bodyguard: float = 0.4
    support: float = 0.3
    rush: float = 0.2
    challenger: float = 0.2
    reckless: float = -0.6
    drying: float = -0.3
    item: float = 0.7
    # Resources.
    hand_card: float = 0.25
    hand_quality: float = 0.35
    unspent_ink: float = -0.15
    # Marginal value of the nth card in the inkwell.  Steeply diminishing: the
    # early ink drops are worth far more than the card they cost, the late ones
    # are not, which is what makes "ink every turn, then stop" fall out.
    ink_curve: tuple = (4.0, 3.6, 3.2, 2.8, 2.4, 1.8, 1.2, 0.6, 0.3, 0.2, 0.1)

    def lore_score(self, lore):
        return self.lore * lore + self.lore_curve * lore * lore

    def ink_score(self, total):
        curve = self.ink_curve
        if not curve:
            return 0.0
        return sum(curve[:total]) + curve[-1] * max(0, total - len(curve))


#: The default inkwell curve, exposed for experiments.
DIMINISHING_INK = Weights().ink_curve

DEFAULT_WEIGHTS = Weights()


def character_value(game, character, weights=DEFAULT_WEIGHTS):
    remaining = game.remaining_willpower(character)
    if remaining <= 0:
        return 0.0
    keywords = game.keywords_of(character)
    value = weights.character_base
    value += weights.character_cost * character.card.cost
    value += weights.character_lore * character.card.lore
    value += weights.character_strength * game.strength_of(character)
    value += weights.character_willpower * remaining
    if keywords.get(EVASIVE):
        value += weights.evasive
    if keywords.get(WARD):
        value += weights.ward
    if keywords.get(BODYGUARD):
        value += weights.bodyguard
    if keywords.get(SUPPORT):
        value += weights.support
    if keywords.get(RUSH):
        value += weights.rush
    value += weights.challenger * keywords.get(CHALLENGER, 0)
    if keywords.get(RECKLESS):
        value += weights.reckless
    if character.drying:
        value += weights.drying
    return value


def card_quality(card, weights=DEFAULT_WEIGHTS):
    """Rough value of a card sitting in hand (used for inking and discarding)."""
    if card.is_character:
        value = (weights.character_lore * card.lore
                 + weights.character_strength * card.strength
                 + weights.character_willpower * card.willpower)
        for keyword, amount in card.keywords.items():
            if keyword == CHALLENGER:
                value += weights.challenger * amount
            elif keyword == EVASIVE:
                value += weights.evasive
            elif keyword == WARD:
                value += weights.ward
            elif keyword in (BODYGUARD, SUPPORT, RUSH):
                value += 0.3
        return value
    # Actions and items: judge them by what they do.
    from .effects import (BanishChosenCharacter, DealDamage,
                          DealDamageToEachOpposing, DrawCards,
                          ReturnChosenCharacterToHand)
    value = 1.5 + 0.25 * card.cost
    for ability in card.abilities:
        effect = getattr(ability, "effect", None)
        if isinstance(effect, (BanishChosenCharacter, DealDamageToEachOpposing)):
            value += 3.0
        elif isinstance(effect, DealDamage):
            value += 1.0 + 0.6 * effect.amount
        elif isinstance(effect, ReturnChosenCharacterToHand):
            value += 2.0
        elif isinstance(effect, DrawCards):
            value += 0.8 * effect.count
    return value


def board_value(game, player, weights=DEFAULT_WEIGHTS):
    value = sum(character_value(game, c, weights) for c in player.characters)
    value += weights.item * len(player.items)
    return value


def hand_value(player, weights=DEFAULT_WEIGHTS):
    """Cards in hand are worth having, but the good ones are worth more.

    Making the value card-specific is what lets the AI work out *which* card to
    put in the inkwell: it inks the one it would miss least.
    """
    return sum(weights.hand_card + weights.hand_quality * card_quality(card, weights)
               for card in player.hand)


def evaluate(game, index, weights=DEFAULT_WEIGHTS):
    """Score the position from ``index``'s point of view."""
    if game.winner is not None:
        return WIN_SCORE if game.winner == index else -WIN_SCORE
    me = game.players[index]
    them = game.players[1 - index]
    score = weights.lore_score(me.lore) - weights.lore_score(them.lore)
    score += board_value(game, me, weights) - board_value(game, them, weights)
    score += hand_value(me, weights) - hand_value(them, weights)
    score += weights.ink_score(me.total_ink) - weights.ink_score(them.total_ink)
    # Ink left unspent at the end of your own turn is wasted tempo.
    if game.current_player is me:
        score += weights.unspent_ink * me.available_ink
    return score
