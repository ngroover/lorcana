"""Every card in the three First Chapter starter decks, with its abilities.

Card numbers follow the printed collector numbers (``n/204``).  Names, stats and
costs match the deck lists the simulator ships with; the abilities below
implement the printed text.
"""

from __future__ import annotations

from .abilities import ActivatedAbility, Event, TriggeredAbility, on_play, on_quest
from .cards import (BODYGUARD, CHALLENGER, Card, CardType, EVASIVE, RUSH,
                    SHIFT, SINGER, SUPPORT, WARD)
from .effects import (ANY, BanishChosenCharacter, BanishChosenItem, DealDamage,
                      DealDamageToEachOpposing, DrawCards, DrawThenDiscard,
                      GainLore, LookAtTopTakeOne, ModifyStrength,
                      OPPOSING, OpponentsLoseLore, PutTopCardIntoInkwell,
                      QuestDrainThisTurn, ReadyChosenCharacter,
                      ReadyOtherPrincesses, RemoveDamage,
                      RemoveDamageFromEachOfYourCharacters,
                      ReturnBanishedCardToHand,
                      ReturnCharacterFromDiscardToHand,
                      ReturnChosenCharacterToHand, ScryTopCard, Sequence,
                      SelfToInkwell, SetFlagNextTurn,
                      ShuffleCardFromAnyDiscardIntoDeck)
from .statics import (CannotSingSongs, GrantKeywordToYourNamed,
                      GrantKeywordToYourOtherCharacters,
                      SelfKeywordDuringYourTurn,
                      SelfKeywordWhileOtherCharacter, TraitCostReduction)

ALL_CARDS = {}


def _register(card):
    if card.id in ALL_CARDS:
        raise ValueError(f"duplicate card id {card.id}")
    ALL_CARDS[card.id] = card
    return card


def character(number, name, version, cost, color, inkable, strength, willpower,
              lore, traits=(), keywords=None, text="", abilities=()):
    return _register(Card(id=f"{number}/204", name=name, version=version,
                          type=CardType.CHARACTER, cost=cost, color=color,
                          inkable=inkable, strength=strength, willpower=willpower,
                          lore=lore, traits=tuple(traits),
                          keywords=dict(keywords or {}), text=text,
                          abilities=tuple(abilities)))


def action_card(number, name, cost, color, inkable, text, abilities=(), traits=()):
    return _register(Card(id=f"{number}/204", name=name, type=CardType.ACTION,
                          cost=cost, color=color, inkable=inkable, text=text,
                          traits=tuple(traits), abilities=tuple(abilities)))


def song(number, name, cost, color, inkable, text, abilities=()):
    return action_card(number, name, cost, color, inkable, text, abilities,
                       traits=("Song",))


def item(number, name, cost, color, inkable, text, abilities=()):
    return _register(Card(id=f"{number}/204", name=name, type=CardType.ITEM,
                          cost=cost, color=color, inkable=inkable, text=text,
                          abilities=tuple(abilities)))


# ==========================================================================
# Amber / Amethyst starter deck
# ==========================================================================

OLAF = character(52, "Olaf", "Friendly Snowman", 1, "amethyst", True, 1, 3, 1,
                 ("Storyborn", "Ally"))

PASCAL = character(
    53, "Pascal", "Rapunzel's Companion", 1, "amethyst", True, 1, 1, 1,
    ("Storyborn", "Ally"),
    text="While you have another character in play, this character gains Evasive.",
    abilities=(SelfKeywordWhileOtherCharacter(keyword=EVASIVE),))

STITCH_NEW_DOG = character(22, "Stitch", "New Dog", 1, "amber", True, 2, 2, 1,
                           ("Storyborn", "Hero", "Alien"))

HEIHEI = character(7, "HeiHei", "Boat Snack", 1, "amber", True, 1, 2, 1,
                   ("Storyborn", "Ally"), {SUPPORT: True}, text="Support")

DINGLEHOPPER = item(
    32, "Dinglehopper", 1, "amber", True,
    "Exert - Remove up to 1 damage from chosen character.",
    abilities=(ActivatedAbility(effect=RemoveDamage(1, ANY),
                                text="Remove up to 1 damage from chosen character"),))

CONTROL_YOUR_TEMPER = action_card(
    26, "Control Your Temper!", 1, "amber", True,
    "Chosen character gets -2 strength this turn.",
    abilities=(on_play(ModifyStrength(-2, ANY)),))

BE_OUR_GUEST = song(
    25, "Be Our Guest", 2, "amber", True,
    "Look at the top 4 cards of your deck. You may reveal a character card and "
    "put it into your hand. Put the rest on the bottom of your deck.",
    abilities=(on_play(LookAtTopTakeOne(4, character_only=True, optional=True)),))

DR_FACILIER_CHARLATAN = character(
    38, "Dr. Facilier", "Charlatan", 2, "amethyst", True, 0, 4, 1,
    ("Storyborn", "Villain", "Sorcerer"), {CHALLENGER: 2}, text="Challenger +2")

MAGIC_BROOM = character(
    47, "Magic Broom", "Bucket Brigade", 2, "amethyst", True, 2, 2, 1,
    ("Dreamborn", "Broom"),
    text="When you play this character, you may shuffle a card from any discard "
         "into its player's deck.",
    abilities=(TriggeredAbility(Event.ON_PLAY,
                                ShuffleCardFromAnyDiscardIntoDeck(),
                                optional=True,
                                text="Shuffle a card from a discard into its deck?"),))

MINNIE_MOUSE = character(13, "Minnie Mouse", "Beloved Princess", 2, "amber", True,
                         2, 3, 1, ("Dreamborn", "Princess"))

YZMA = character(
    60, "Yzma", "Alchemist", 2, "amethyst", True, 2, 2, 1,
    ("Dreamborn", "Villain", "Sorcerer"),
    text="Whenever this character quests, look at the top card of your deck. "
         "Put it on either the top or the bottom of your deck.",
    abilities=(on_quest(ScryTopCard()),))

FRIENDS_ON_THE_OTHER_SIDE = song(
    64, "Friends on the Other Side", 3, "amethyst", True, "Draw 2 cards.",
    abilities=(on_play(DrawCards(2)),))

MALEFICENT_SORCERESS = character(
    49, "Maleficent", "Sorceress", 3, "amethyst", True, 2, 2, 1,
    ("Storyborn", "Villain", "Sorcerer"),
    text="When you play this character, you may draw a card.",
    abilities=(TriggeredAbility(Event.ON_PLAY, DrawCards(1), optional=True,
                                text="Draw a card?"),))

MAXIMUS = character(
    11, "Maximus", "Relentless Pursuer", 3, "amber", True, 3, 3, 1,
    ("Dreamborn", "Ally"),
    text="When you play this character, chosen character gets -2 strength this turn.",
    abilities=(on_play(ModifyStrength(-2, ANY)),))

MICKEY_TRUE_FRIEND = character(12, "Mickey Mouse", "True Friend", 3, "amber", True,
                               3, 3, 2, ("Storyborn", "Hero"))

PART_OF_YOUR_WORLD = song(
    30, "Part of Your World", 3, "amber", False,
    "Return a character card from your discard to your hand.",
    abilities=(on_play(ReturnCharacterFromDiscardToHand()),))

RAFIKI = character(54, "Rafiki", "Mysterious Sage", 3, "amethyst", False, 3, 3, 1,
                   ("Dreamborn", "Mentor", "Sorcerer"), {RUSH: True}, text="Rush")

THE_WARDROBE = character(57, "The Wardrobe", "Belle's Confidant", 3, "amber", True,
                         3, 4, 1, ("Dreamborn", "Ally"))

ARIEL_HUMAN_LEGS = character(
    1, "Ariel", "On Human Legs", 4, "amber", True, 3, 4, 2,
    ("Storyborn", "Hero", "Princess"),
    text="This character can't sing songs.",
    abilities=(CannotSingSongs(),))

CINDERELLA_GENTLE = character(
    3, "Cinderella", "Gentle and Kind", 4, "amber", True, 2, 5, 2,
    ("Storyborn", "Hero", "Princess"), {SINGER: 5},
    text="Singer 5. Exert - Remove up to 3 damage from chosen Princess character.",
    abilities=(ActivatedAbility(effect=RemoveDamage(3, ANY, trait="Princess"),
                                text="Remove up to 3 damage from chosen Princess"),))

HADES = character(
    6, "Hades", "Lord of the Underworld", 4, "amber", False, 3, 2, 1,
    ("Storyborn", "Villain", "Deity"),
    text="When you play this character, return a character card from your discard "
         "pile to your hand.",
    abilities=(on_play(ReturnCharacterFromDiscardToHand()),))

HAKUNA_MATATA = song(
    27, "Hakuna Matata", 4, "amber", True,
    "Remove up to 3 damage from each of your characters.",
    abilities=(on_play(RemoveDamageFromEachOfYourCharacters(3)),))

JAFAR_WICKED = character(45, "Jafar", "Wicked Sorcerer", 4, "amethyst", True, 2, 5, 1,
                         ("Dreamborn", "Villain", "Sorcerer"), {CHALLENGER: 3},
                         text="Challenger +3")

JETSAM = character(
    46, "Jetsam", "Ursula's Spy", 4, "amethyst", True, 3, 3, 1,
    ("Storyborn", "Ally"), {EVASIVE: True},
    text="Evasive. Your characters named Flotsam gain Evasive.",
    abilities=(GrantKeywordToYourNamed(name="Flotsam", keyword=EVASIVE),))

MICKEY_WAYWARD_SORCERER = character(
    51, "Mickey Mouse", "Wayward Sorcerer", 4, "amethyst", True, 3, 4, 2,
    ("Dreamborn", "Sorcerer"),
    text="You pay 1 less to play Broom characters. Whenever one of your Broom "
         "characters is banished in a challenge, you may return that card to your hand.",
    abilities=(TraitCostReduction(trait="Broom", amount=1),
               TriggeredAbility(Event.OTHER_BANISHED_IN_CHALLENGE,
                                ReturnBanishedCardToHand(), optional=True,
                                trait_filter="Broom",
                                text="Return the banished Broom to your hand?")))

FLOTSAM = character(
    43, "Flotsam", "Ursula's Spy", 5, "amethyst", False, 3, 4, 2,
    ("Storyborn", "Ally"), {RUSH: True},
    text="Rush. Your characters named Jetsam gain Rush.",
    abilities=(GrantKeywordToYourNamed(name="Jetsam", keyword=RUSH),))

MOANA = character(
    14, "Moana", "Of Motunui", 5, "amber", True, 1, 6, 3,
    ("Storyborn", "Hero", "Princess"),
    text="Whenever this character quests, you may ready your other Princess "
         "characters. They can't quest for the rest of this turn.",
    abilities=(TriggeredAbility(Event.ON_QUEST, ReadyOtherPrincesses(), optional=True,
                                text="Ready your other Princess characters?"),))

SVEN = character(55, "Sven", "Official Ice Deliverer", 6, "amethyst", True, 5, 7, 1,
                 ("Storyborn", "Ally"))

DR_FACILIER_AGENT = character(
    37, "Dr. Facilier", "Agent Provocateur", 7, "amethyst", False, 4, 5, 3,
    ("Floodborn", "Villain", "Sorcerer"), {SHIFT: 5},
    text="Shift 5. Whenever one of your other characters is banished in a "
         "challenge, you may return that card to your hand.",
    abilities=(TriggeredAbility(Event.OTHER_BANISHED_IN_CHALLENGE,
                                ReturnBanishedCardToHand(), optional=True,
                                text="Return the banished character to your hand?"),))


# ==========================================================================
# Sapphire / Steel starter deck
# ==========================================================================

CAPTAIN_HOOK_DUELIST = character(
    174, "Captain Hook", "Forceful Duelist", 1, "steel", True, 1, 2, 1,
    ("Dreamborn", "Villain", "Pirate", "Captain"), {CHALLENGER: 2},
    text="Challenger +2")

DEVELOP_YOUR_BRAIN = action_card(
    161, "Develop Your Brain", 1, "sapphire", True,
    "Look at the top 2 cards of your deck. Put one into your hand and the other "
    "on the bottom of your deck.",
    abilities=(on_play(LookAtTopTakeOne(2)),))

FIRE_THE_CANNONS = action_card(
    197, "Fire the Cannons!", 1, "steel", False,
    "Deal 2 damage to chosen character.",
    abilities=(on_play(DealDamage(2, ANY)),))

FLOUNDER = character(145, "Flounder", "Voice of Reason", 1, "sapphire", True, 2, 2, 1,
                     ("Storyborn", "Ally"))

GOONS = character(179, "Goons", "Maleficent's Underlings", 1, "steel", True, 2, 2, 1,
                  ("Storyborn", "Ally"))

MAGIC_GOLDEN_FLOWER = item(
    169, "Magic Golden Flower", 1, "sapphire", True,
    "Banish this item - Remove up to 3 damage from chosen character.",
    abilities=(ActivatedAbility(effect=RemoveDamage(3, ANY), banish_self=True,
                                text="Remove up to 3 damage from chosen character"),))

AURORA_REGAL = character(140, "Aurora", "Regal Princess", 2, "sapphire", True, 2, 2, 2,
                         ("Storyborn", "Hero", "Princess"))

COCONUT_BASKET = item(
    166, "Coconut Basket", 2, "sapphire", True,
    "Whenever you play a character, you may remove up to 2 damage from chosen "
    "character.",
    abilities=(TriggeredAbility(Event.YOU_PLAY_CHARACTER, RemoveDamage(2, ANY),
                                optional=True,
                                text="Remove up to 2 damage from chosen character?"),))

FRYING_PAN = item(
    202, "Frying Pan", 2, "steel", True,
    "Banish this item - Chosen character can't challenge during their next turn.",
    abilities=(ActivatedAbility(effect=SetFlagNextTurn("cant_challenge", ANY),
                                banish_self=True,
                                text="Chosen character can't challenge next turn"),))

GRAMMA_TALA = character(
    146, "Gramma Tala", "Storyteller", 2, "sapphire", True, 1, 1, 1,
    ("Storyborn", "Mentor"),
    text="When this character is banished, you may put this card into your "
         "inkwell facedown and exerted.",
    abilities=(TriggeredAbility(Event.ON_BANISHED, SelfToInkwell(), optional=True,
                                text="Put Gramma Tala into your inkwell?"),))

ONE_JUMP_AHEAD = song(
    164, "One Jump Ahead", 2, "sapphire", False,
    "Put the top card of your deck into your inkwell facedown and exerted.",
    abilities=(on_play(PutTopCardIntoInkwell()),))

PRINCE_ERIC = character(187, "Prince Eric", "Dashing and Brave", 2, "steel", True,
                        1, 3, 1, ("Storyborn", "Hero", "Prince"), {CHALLENGER: 2},
                        text="Challenger +2")

RANSACK = action_card(
    199, "Ransack", 2, "steel", True, "Draw 2 cards, then choose and discard 2 cards.",
    abilities=(on_play(DrawThenDiscard(2, 2)),))

HERCULES = character(181, "Hercules", "True Hero", 3, "steel", True, 3, 3, 1,
                     ("Dreamborn", "Hero", "Prince"), {BODYGUARD: True},
                     text="Bodyguard")

JASMINE_DISGUISED = character(148, "Jasmine", "Disguised", 3, "sapphire", True,
                              3, 3, 2, ("Storyborn", "Princess"))

KRISTOFF = character(182, "Kristoff", "Official Ice Master", 3, "steel", True,
                     3, 3, 2, ("Storyborn", "Ally"))

MICKEY_DETECTIVE = character(
    154, "Mickey Mouse", "Detective", 3, "sapphire", False, 1, 3, 1,
    ("Dreamborn", "Hero", "Detective"),
    text="When you play this character, you may put the top card of your deck "
         "into your inkwell facedown and exerted.",
    abilities=(on_play(PutTopCardIntoInkwell(optional=True)),))

SMASH = action_card(
    200, "Smash", 3, "steel", True, "Deal 3 damage to chosen character.",
    abilities=(on_play(DealDamage(3, ANY)),))

AURORA_BRIAR_ROSE = character(
    138, "Aurora", "Briar Rose", 4, "sapphire", True, 2, 5, 1,
    ("Storyborn", "Hero", "Princess"),
    text="When you play this character, chosen character gets -2 strength this turn.",
    abilities=(on_play(ModifyStrength(-2, ANY)),))

MALEFICENT_SINISTER = character(150, "Maleficent", "Sinister Visitor", 4, "sapphire",
                                True, 3, 4, 2,
                                ("Storyborn", "Villain", "Sorcerer"))

AURORA_DREAMING_GUARDIAN = character(
    139, "Aurora", "Dreaming Guardian", 5, "sapphire", True, 3, 5, 2,
    ("Floodborn", "Hero", "Princess"), {SHIFT: 3},
    text="Shift 3. Your other characters gain Ward.",
    abilities=(GrantKeywordToYourOtherCharacters(keyword=WARD),))

BEAST_HARDHEADED = character(
    172, "Beast", "Hardheaded", 5, "steel", True, 4, 4, 2,
    ("Storyborn", "Hero", "Prince"),
    text="When you play this character, you may banish chosen item.",
    abilities=(on_play(BanishChosenItem(optional=True)),))

GRAB_YOUR_SWORD = song(
    198, "Grab Your Sword", 5, "steel", False,
    "Deal 2 damage to each opposing character.",
    abilities=(on_play(DealDamageToEachOpposing(2)),))

MALEFICENT_UNINVITED = character(151, "Maleficent", "Uninvited", 5, "sapphire", True,
                                 3, 6, 3, ("Dreamborn", "Villain", "Sorcerer"))

SIMBA_RIGHTFUL_HEIR = character(
    190, "Simba", "Rightful Heir", 5, "steel", False, 3, 5, 2,
    ("Storyborn", "Hero", "Prince"),
    text="During your turn, whenever this character banishes another character "
         "in a challenge, you gain 1 lore.",
    abilities=(TriggeredAbility(Event.BANISHES_IN_CHALLENGE, GainLore(1),
                                your_turn_only=True, text="Gain 1 lore"),))

MUFASA = character(155, "Mufasa", "King of the Pride Lands", 6, "sapphire", True,
                   4, 6, 3, ("Storyborn", "Mentor", "King"))

SCAR_MASTERMIND = character(
    158, "Scar", "Mastermind", 6, "sapphire", True, 5, 4, 2,
    ("Storyborn", "Villain"),
    text="When you play this character, chosen opposing character gets -5 "
         "strength this turn.",
    abilities=(on_play(ModifyStrength(-5, OPPOSING)),))

SIMBA_RETURNED_KING = character(
    189, "Simba", "Returned King", 7, "steel", True, 4, 6, 2,
    ("Storyborn", "Hero", "King"), {CHALLENGER: 4},
    text="Challenger +4. During your turn, this character gains Evasive.",
    abilities=(SelfKeywordDuringYourTurn(keyword=EVASIVE),))

MAUI = character(185, "Maui", "Demigod", 8, "steel", True, 8, 8, 3,
                 ("Storyborn", "Hero", "Deity"))


# ==========================================================================
# Ruby / Emerald starter deck
# ==========================================================================

DUKE_OF_WESELTON = character(73, "Duke of Weselton", "Opportunistic Official", 1,
                             "emerald", True, 2, 2, 1, ("Storyborn", "Villain"))

HES_GOT_A_SWORD = action_card(
    132, "He's Got a Sword!", 1, "ruby", True,
    "Chosen character gets +2 strength this turn.",
    abilities=(on_play(ModifyStrength(2, ANY)),))

SERGEANT_TIBBS = character(124, "Sergeant Tibbs", "Courageous Cat", 1, "ruby", True,
                           2, 2, 1, ("Storyborn", "Ally"))

SHIELD_OF_VIRTUE = item(
    135, "Shield of Virtue", 1, "ruby", True,
    "Exert, 3 ink - Ready chosen character. They can't quest for the rest of this turn.",
    abilities=(ActivatedAbility(effect=ReadyChosenCharacter(ANY, cant_quest=True),
                                ink_cost=3,
                                text="Ready chosen character (can't quest this turn)"),))

STAMPEDE = action_card(
    96, "Stampede", 1, "emerald", False,
    "Deal 2 damage to chosen damaged character.",
    abilities=(on_play(DealDamage(2, ANY, damaged_only=True)),))

VICIOUS_BETRAYAL = action_card(
    100, "Vicious Betrayal", 1, "emerald", True,
    "Chosen character gets +2 strength this turn. If a Villain character is "
    "chosen, they get +3 instead.",
    abilities=(on_play(ModifyStrength(2, ANY, villain_amount=3)),))

ALADDIN_PRINCE_ALI = character(69, "Aladdin", "Prince Ali", 2, "emerald", True,
                               2, 2, 1, ("Storyborn", "Hero", "Prince"),
                               {WARD: True}, text="Ward")

CRUELLA_DE_VIL = character(
    72, "Cruella De Vil", "Miserable As Usual", 2, "emerald", True, 1, 3, 1,
    ("Storyborn", "Villain"),
    text="When this character is challenged and banished, you may return chosen "
         "character to their player's hand.",
    abilities=(TriggeredAbility(Event.CHALLENGED_AND_BANISHED,
                                ReturnChosenCharacterToHand(ANY), optional=True,
                                text="Return chosen character to their hand?"),))

DONALD_DUCK = character(108, "Donald Duck", "Boisterous Fowl", 2, "ruby", True,
                        2, 3, 1, ("Storyborn",))

LEFOU = character(
    112, "Lefou", "Instigator", 2, "ruby", True, 2, 2, 1, ("Dreamborn", "Ally"),
    text="When you play this character, ready chosen character. They can't quest "
         "for the rest of this turn.",
    abilities=(on_play(ReadyChosenCharacter(ANY, cant_quest=True)),))

MEGARA = character(
    87, "Megara", "Pulling the Strings", 2, "emerald", True, 2, 1, 1,
    ("Dreamborn", "Ally"),
    text="When you play this character, chosen character gets +2 strength this turn.",
    abilities=(on_play(ModifyStrength(2, ANY)),))

STOLEN_SCIMITAR = item(
    102, "Stolen Scimitar", 2, "emerald", True,
    "Exert - Chosen character gets +1 strength this turn. If a character named "
    "Aladdin is chosen, he gets +2 strength instead.",
    abilities=(ActivatedAbility(
        effect=ModifyStrength(1, ANY, name_bonus=("Aladdin", 2)),
        text="Chosen character gets +1 strength (+2 for Aladdin)"),))

ALADDIN_STREET_RAT = character(
    105, "Aladdin", "Street Rat", 3, "ruby", True, 2, 2, 1,
    ("Storyborn", "Hero"),
    text="When you play this character, each opponent loses 1 lore.",
    abilities=(on_play(OpponentsLoseLore(1)),))

HORACE = character(79, "Horace", "No-Good Scoundrel", 3, "emerald", True, 4, 3, 1,
                   ("Storyborn", "Ally"))

IAGO = character(
    80, "Iago", "Loud-Mouthed Parrot", 3, "emerald", True, 1, 4, 1,
    ("Storyborn", "Ally"),
    text="Exert - Chosen character gains Reckless during their next turn.",
    abilities=(ActivatedAbility(effect=SetFlagNextTurn("reckless", ANY),
                                text="Chosen character gains Reckless next turn"),))

JASPER = character(
    81, "Jasper", "Common Crook", 3, "emerald", True, 2, 4, 1,
    ("Storyborn", "Ally"),
    text="Whenever this character quests, chosen opposing character can't quest "
         "during their next turn.",
    abilities=(on_quest(SetFlagNextTurn("cant_quest", OPPOSING)),))

MICKEY_STEAMBOAT = character(89, "Mickey Mouse", "Steamboat Pilot", 3, "emerald",
                             True, 3, 4, 1, ("Storyborn", "Hero", "Captain"))

MOTHER_KNOWS_BEST = song(
    95, "Mother Knows Best", 3, "emerald", False,
    "Return chosen character to their player's hand.",
    abilities=(on_play(ReturnChosenCharacterToHand(ANY)),))

PETER_PAN = character(91, "Peter Pan", "Never Landing", 3, "emerald", True, 3, 2, 1,
                      ("Dreamborn", "Hero"), {EVASIVE: True}, text="Evasive")

PONGO = character(120, "Pongo", "Ol' Rascal", 4, "ruby", True, 2, 3, 2,
                  ("Storyborn", "Hero"), {EVASIVE: True}, text="Evasive")

SCAR_FIERY_USURPER = character(122, "Scar", "Fiery Usurper", 4, "ruby", True,
                               5, 3, 1, ("Dreamborn", "Villain"))

THE_CAPTAIN = character(106, "Captain", "Colonel's Lieutenant", 5, "ruby", True,
                        6, 5, 1, ("Storyborn", "Ally", "Captain"))

DRAGON_FIRE = action_card(
    130, "Dragon Fire", 5, "ruby", False, "Banish chosen character.",
    abilities=(on_play(BanishChosenCharacter(ANY)),))

MAD_HATTER = character(
    86, "Mad Hatter", "Gracious Host", 5, "emerald", True, 2, 4, 3,
    ("Storyborn",),
    text="Whenever this character is challenged, you may draw a card.",
    abilities=(TriggeredAbility(Event.CHALLENGED, DrawCards(1), optional=True,
                                text="Draw a card?"),))

STEAL_FROM_THE_RICH = action_card(
    97, "Steal from the Rich", 5, "emerald", False,
    "Whenever one of your characters quests this turn, each opponent loses 1 lore.",
    abilities=(on_play(QuestDrainThisTurn(1)),))

RAPUNZEL_LETTING_DOWN = character(
    121, "Rapunzel", "Letting Down Her Hair", 6, "ruby", False, 5, 4, 2,
    ("Dreamborn", "Hero", "Princess"),
    text="When you play this character, each opponent loses 1 lore.",
    abilities=(on_play(OpponentsLoseLore(1)),))

STITCH_ABOMINATION = character(125, "Stitch", "Abomination", 6, "ruby", True,
                               4, 6, 3, ("Storyborn", "Hero", "Alien"))

ALADDIN_HEROIC_OUTLAW = character(
    104, "Aladdin", "Heroic Outlaw", 7, "ruby", True, 5, 5, 2,
    ("Floodborn", "Hero"), {SHIFT: 5},
    text="Shift 5. During your turn, whenever this character banishes another "
         "character in a challenge, you gain 2 lore and each opponent loses 2 lore.",
    abilities=(TriggeredAbility(Event.BANISHES_IN_CHALLENGE,
                                Sequence((GainLore(2), OpponentsLoseLore(2))),
                                your_turn_only=True,
                                text="Gain 2 lore, opponent loses 2 lore"),))
