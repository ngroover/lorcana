"""Abilities: the three shapes of printed ability the starter decks need.

* :class:`StaticAbility` – always-on effects (keyword granting, cost changes).
* :class:`TriggeredAbility` – fires on a game event.
* :class:`ActivatedAbility` – the player pays a cost to use it.

Abilities are immutable and shared with their :class:`~lorcana.cards.Card`.
"""

from __future__ import annotations

from dataclasses import dataclass


class Event:
    """Names of the trigger events the engine raises."""

    ON_PLAY = "on_play"                       # this card was played
    ON_QUEST = "on_quest"                     # this character quested
    ON_BANISHED = "on_banished"               # this character was banished (any cause)
    CHALLENGED = "challenged"                 # this character was challenged
    CHALLENGED_AND_BANISHED = "challenged_and_banished"
    BANISHES_IN_CHALLENGE = "banishes_in_challenge"    # this character banished another
    OTHER_BANISHED_IN_CHALLENGE = "other_banished_in_challenge"
    YOU_PLAY_CHARACTER = "you_play_character"  # controller played a character


@dataclass(frozen=True)
class Ability:
    def __deepcopy__(self, memo):
        return self

    def __copy__(self):
        return self


@dataclass(frozen=True)
class StaticAbility(Ability):
    """Continuous ability.

    Subclasses override the hooks they care about.  Hooks are queried by the
    engine every time it needs the answer, so they always see current state.
    """

    def grant_keywords(self, game, source, character):
        """Extra keywords ``source`` grants ``character`` (a dict or None)."""
        return None

    def cost_modifier(self, game, source, player, card):
        """Ink discount (negative) or surcharge this ability applies."""
        return 0

    def forbids_singing(self, game, source, character):
        return False


@dataclass(frozen=True)
class TriggeredAbility(Ability):
    event: str = Event.ON_PLAY
    effect: object = None
    optional: bool = False
    text: str = ""
    # Restrict OTHER_BANISHED_IN_CHALLENGE style triggers to a trait.
    trait_filter: str = ""
    your_turn_only: bool = False

    def matches(self, game, ctx):
        if self.trait_filter:
            other = ctx.get("other")
            if other is None or not other.card.has_trait(self.trait_filter):
                return False
        if self.your_turn_only and ctx.get("player") is not game.current_player:
            return False
        return True


@dataclass(frozen=True)
class ActivatedAbility(Ability):
    effect: object = None
    exert: bool = True        # requires exerting the source
    banish_self: bool = False  # requires banishing the source (items)
    ink_cost: int = 0
    text: str = ""

    def cost_description(self):
        parts = []
        if self.banish_self:
            parts.append("Banish this item")
        elif self.exert:
            parts.append("Exert")
        if self.ink_cost:
            parts.append(f"{self.ink_cost} ink")
        return ", ".join(parts)


def on_play(effect, optional=False, text=""):
    return TriggeredAbility(Event.ON_PLAY, effect, optional, text)


def on_quest(effect, optional=False, text=""):
    return TriggeredAbility(Event.ON_QUEST, effect, optional, text)
