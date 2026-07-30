"""Card model for the Lorcana simulator.

Cards are immutable, shared descriptions of a printed card.  Everything that
changes during a game lives on the in-play wrappers in ``state.py`` instead, so
a card object can be shared freely between players, decks and clones of the
game.  ``__deepcopy__`` returns ``self`` for that reason: cloning a game for AI
search must not duplicate the card database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CardType(Enum):
    CHARACTER = "Character"
    ACTION = "Action"
    ITEM = "Item"


# Keyword names.  Boolean keywords map to True, numeric ones to their value.
EVASIVE = "Evasive"
RUSH = "Rush"
WARD = "Ward"
BODYGUARD = "Bodyguard"
SUPPORT = "Support"
RECKLESS = "Reckless"
CHALLENGER = "Challenger"
SINGER = "Singer"
SHIFT = "Shift"

BOOLEAN_KEYWORDS = (EVASIVE, RUSH, WARD, BODYGUARD, SUPPORT, RECKLESS)


def format_keywords(keywords):
    parts = []
    for name in (EVASIVE, RUSH, WARD, BODYGUARD, SUPPORT, RECKLESS):
        if keywords.get(name):
            parts.append(name)
    for name in (CHALLENGER, SINGER, SHIFT):
        value = keywords.get(name)
        if value:
            parts.append(f"{name} +{value}" if name == CHALLENGER else f"{name} {value}")
    return ", ".join(parts)


@dataclass(frozen=True)
class Card:
    id: str
    name: str
    type: CardType
    cost: int
    color: str
    inkable: bool
    version: str = ""
    text: str = ""
    traits: tuple = ()
    strength: int = 0
    willpower: int = 0
    lore: int = 0
    keywords: dict = field(default_factory=dict)
    abilities: tuple = ()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Card) and self.id == other.id

    def __deepcopy__(self, memo):
        return self

    def __copy__(self):
        return self

    @property
    def is_character(self):
        return self.type is CardType.CHARACTER

    @property
    def is_action(self):
        return self.type is CardType.ACTION

    @property
    def is_item(self):
        return self.type is CardType.ITEM

    @property
    def is_song(self):
        return "Song" in self.traits

    @property
    def full_name(self):
        return f"{self.name} - {self.version}" if self.version else self.name

    def has_trait(self, trait):
        return trait in self.traits

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<{self.full_name}>"

    def describe(self):
        """Multi-line description used by the command line interface."""
        head = f"{self.full_name} [{self.color} {self.cost}"
        head += ", inkable]" if self.inkable else ", not inkable]"
        if self.is_character:
            head += f" {self.strength}/{self.willpower} {self.lore} lore"
        bits = [head]
        kw = format_keywords(self.keywords)
        if kw:
            bits.append(f"    {kw}")
        if self.text:
            bits.append(f"    {self.text}")
        return "\n".join(bits)
