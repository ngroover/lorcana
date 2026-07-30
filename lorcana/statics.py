"""Static (always-on) abilities used by the starter deck cards."""

from __future__ import annotations

from dataclasses import dataclass

from .abilities import StaticAbility


@dataclass(frozen=True)
class SelfKeywordWhileOtherCharacter(StaticAbility):
    """Pascal: while you have another character in play, this gains a keyword."""

    keyword: str = "Evasive"

    def grant_keywords(self, game, source, character):
        if character is not source:
            return None
        owner = game.owner_of(source)
        if len(owner.characters) >= 2:
            return {self.keyword: True}
        return None


@dataclass(frozen=True)
class SelfKeywordDuringYourTurn(StaticAbility):
    """Simba - Returned King: during your turn, this character gains Evasive."""

    keyword: str = "Evasive"

    def grant_keywords(self, game, source, character):
        if character is not source:
            return None
        if game.owner_of(source) is game.current_player:
            return {self.keyword: True}
        return None


@dataclass(frozen=True)
class GrantKeywordToYourNamed(StaticAbility):
    """Jetsam / Flotsam: your characters with a given name gain a keyword."""

    name: str = ""
    keyword: str = "Evasive"

    def grant_keywords(self, game, source, character):
        if character is source or character.card.name != self.name:
            return None
        if character.owner_index != source.owner_index:
            return None
        return {self.keyword: True}


@dataclass(frozen=True)
class GrantKeywordToYourOtherCharacters(StaticAbility):
    """Aurora - Dreaming Guardian: your other characters gain Ward."""

    keyword: str = "Ward"

    def grant_keywords(self, game, source, character):
        if character is source:
            return None
        if character.owner_index != source.owner_index:
            return None
        return {self.keyword: True}


@dataclass(frozen=True)
class TraitCostReduction(StaticAbility):
    """Mickey Mouse - Wayward Sorcerer: you pay 1 less to play Broom characters."""

    trait: str = ""
    amount: int = 1

    def cost_modifier(self, game, source, player, card):
        if card.has_trait(self.trait):
            return -self.amount
        return 0


@dataclass(frozen=True)
class CannotSingSongs(StaticAbility):
    """Ariel - On Human Legs: this character can't sing songs."""

    def forbids_singing(self, game, source, character):
        return character is source
