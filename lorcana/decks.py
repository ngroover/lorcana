"""The three Disney Lorcana: The First Chapter starter decks (60 cards each)."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import carddb as db


@dataclass
class Decklist:
    name: str
    cards: list = field(default_factory=list)

    @property
    def colors(self):
        return sorted({card.color for card in self.cards})

    def unique_cards(self):
        seen = {}
        for card in self.cards:
            seen.setdefault(card.id, card)
        return list(seen.values())

    def counts(self):
        counts = {}
        for card in self.cards:
            counts[card] = counts.get(card, 0) + 1
        return counts

    def describe(self):
        lines = [f"{self.name} ({len(self.cards)} cards)"]
        for card, count in sorted(self.counts().items(),
                                  key=lambda kv: (kv[0].cost, kv[0].name)):
            lines.append(f"  {count}x {card.describe().splitlines()[0]}")
        return "\n".join(lines)


def _build(name, entries):
    cards = []
    for count, card in entries:
        cards.extend([card] * count)
    deck = Decklist(name, cards)
    if len(cards) != 60:  # pragma: no cover - guards the deck data
        raise ValueError(f"{name} has {len(cards)} cards, expected 60")
    return deck


AMBER_AMETHYST = _build("Amber/Amethyst (The First Chapter starter)", [
    (3, db.OLAF), (2, db.PASCAL), (3, db.STITCH_NEW_DOG), (2, db.HEIHEI),
    (3, db.DINGLEHOPPER), (2, db.CONTROL_YOUR_TEMPER),
    (2, db.BE_OUR_GUEST), (2, db.DR_FACILIER_CHARLATAN), (3, db.MAGIC_BROOM),
    (3, db.MINNIE_MOUSE), (2, db.YZMA),
    (3, db.FRIENDS_ON_THE_OTHER_SIDE), (2, db.MALEFICENT_SORCERESS), (2, db.MAXIMUS),
    (3, db.MICKEY_TRUE_FRIEND), (1, db.PART_OF_YOUR_WORLD), (3, db.RAFIKI),
    (3, db.THE_WARDROBE),
    (2, db.ARIEL_HUMAN_LEGS), (2, db.CINDERELLA_GENTLE), (1, db.HADES),
    (2, db.HAKUNA_MATATA), (2, db.JAFAR_WICKED), (2, db.JETSAM),
    (1, db.MICKEY_WAYWARD_SORCERER),
    (1, db.FLOTSAM), (1, db.MOANA), (1, db.SVEN), (1, db.DR_FACILIER_AGENT),
])

SAPPHIRE_STEEL = _build("Sapphire/Steel (The First Chapter starter)", [
    (3, db.CAPTAIN_HOOK_DUELIST), (3, db.DEVELOP_YOUR_BRAIN),
    (3, db.FIRE_THE_CANNONS), (2, db.FLOUNDER), (2, db.GOONS),
    (2, db.MAGIC_GOLDEN_FLOWER),
    (3, db.AURORA_REGAL), (3, db.COCONUT_BASKET), (2, db.FRYING_PAN),
    (2, db.GRAMMA_TALA), (2, db.ONE_JUMP_AHEAD), (2, db.PRINCE_ERIC), (2, db.RANSACK),
    (2, db.HERCULES), (2, db.JASMINE_DISGUISED), (2, db.KRISTOFF),
    (3, db.MICKEY_DETECTIVE), (2, db.SMASH),
    (3, db.AURORA_BRIAR_ROSE), (3, db.MALEFICENT_SINISTER),
    (1, db.AURORA_DREAMING_GUARDIAN), (2, db.BEAST_HARDHEADED),
    (1, db.GRAB_YOUR_SWORD), (1, db.MALEFICENT_UNINVITED),
    (2, db.SIMBA_RIGHTFUL_HEIR),
    (2, db.MUFASA), (1, db.SCAR_MASTERMIND),
    (1, db.SIMBA_RETURNED_KING), (1, db.MAUI),
])

RUBY_EMERALD = _build("Ruby/Emerald (The First Chapter starter)", [
    (2, db.DUKE_OF_WESELTON), (2, db.HES_GOT_A_SWORD), (3, db.SERGEANT_TIBBS),
    (2, db.SHIELD_OF_VIRTUE), (2, db.STAMPEDE), (2, db.VICIOUS_BETRAYAL),
    (2, db.ALADDIN_PRINCE_ALI), (1, db.CRUELLA_DE_VIL), (2, db.DONALD_DUCK),
    (1, db.LEFOU), (3, db.MEGARA), (2, db.STOLEN_SCIMITAR),
    (3, db.ALADDIN_STREET_RAT), (3, db.HORACE), (1, db.IAGO), (2, db.JASPER),
    (3, db.MICKEY_STEAMBOAT), (3, db.MOTHER_KNOWS_BEST), (2, db.PETER_PAN),
    (3, db.PONGO), (2, db.SCAR_FIERY_USURPER),
    (2, db.THE_CAPTAIN), (3, db.DRAGON_FIRE), (3, db.MAD_HATTER),
    (1, db.STEAL_FROM_THE_RICH),
    (3, db.RAPUNZEL_LETTING_DOWN), (1, db.STITCH_ABOMINATION),
    (1, db.ALADDIN_HEROIC_OUTLAW),
])

DECKLISTS = [AMBER_AMETHYST, SAPPHIRE_STEEL, RUBY_EMERALD]


def by_name(text):
    """Look a deck up by a case-insensitive prefix or index (1-based)."""
    if text is None:
        return None
    text = str(text).strip().lower()
    if text.isdigit():
        index = int(text) - 1
        if 0 <= index < len(DECKLISTS):
            return DECKLISTS[index]
        return None
    for deck in DECKLISTS:
        if deck.name.lower().startswith(text):
            return deck
    for deck in DECKLISTS:
        if text in deck.name.lower():
            return deck
    return None
