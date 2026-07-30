"""Mutable game state: players and the cards they have in play.

In-play wrappers compare by identity (``eq=False``): two copies of the same card
in play are different objects and must never be treated as equal, even when all
their fields happen to match.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(eq=False)
class InkCard:
    card: object
    ready: bool = True

    def copy(self):
        return InkCard(self.card, self.ready)


@dataclass(eq=False)
class InPlayCharacter:
    card: object
    uid: int = 0
    owner_index: int = 0
    ready: bool = True
    drying: bool = True          # played this turn: can't quest, challenge or exert
    damage: int = 0
    strength_mod: int = 0        # cleared at end of turn
    cant_quest: bool = False     # this turn
    cant_challenge: bool = False  # this turn
    extra_keywords: dict = field(default_factory=dict)  # granted for this turn
    pending_flags: dict = field(default_factory=dict)   # applied on controller's next turn
    underneath: list = field(default_factory=list)      # cards covered by Shift

    @property
    def name(self):
        return self.card.name

    def copy(self):
        clone = InPlayCharacter(self.card, self.uid, self.owner_index, self.ready,
                                self.drying, self.damage, self.strength_mod,
                                self.cant_quest, self.cant_challenge)
        if self.extra_keywords:
            clone.extra_keywords = dict(self.extra_keywords)
        if self.pending_flags:
            clone.pending_flags = dict(self.pending_flags)
        if self.underneath:
            clone.underneath = list(self.underneath)
        return clone

    def __str__(self):
        return self.card.full_name


@dataclass(eq=False)
class InPlayItem:
    card: object
    uid: int = 0
    owner_index: int = 0
    ready: bool = True

    @property
    def name(self):
        return self.card.name

    def copy(self):
        return InPlayItem(self.card, self.uid, self.owner_index, self.ready)

    def __str__(self):
        return self.card.full_name


@dataclass(eq=False)
class PlayerState:
    index: int
    name: str
    deck: list = field(default_factory=list)
    hand: list = field(default_factory=list)
    inkwell: list = field(default_factory=list)
    characters: list = field(default_factory=list)
    items: list = field(default_factory=list)
    discard: list = field(default_factory=list)
    lore: int = 0
    inked_this_turn: bool = False
    quest_drain: int = 0          # Steal from the Rich, cleared each turn
    lost_to_empty_deck: bool = False

    def copy(self):
        clone = PlayerState(self.index, self.name)
        clone.deck = list(self.deck)
        clone.hand = list(self.hand)
        clone.inkwell = [ink.copy() for ink in self.inkwell]
        clone.characters = [c.copy() for c in self.characters]
        clone.items = [i.copy() for i in self.items]
        clone.discard = list(self.discard)
        clone.lore = self.lore
        clone.inked_this_turn = self.inked_this_turn
        clone.quest_drain = self.quest_drain
        clone.lost_to_empty_deck = self.lost_to_empty_deck
        return clone

    @property
    def available_ink(self):
        return sum(1 for ink in self.inkwell if ink.ready)

    @property
    def total_ink(self):
        return len(self.inkwell)

    def exert_ink(self, amount):
        for ink in self.inkwell:
            if amount <= 0:
                break
            if ink.ready:
                ink.ready = False
                amount -= 1
        if amount > 0:
            raise ValueError("not enough ink")

    def character_by_uid(self, uid):
        for character in self.characters:
            if character.uid == uid:
                return character
        return None

    def item_by_uid(self, uid):
        for item in self.items:
            if item.uid == uid:
                return item
        return None
