"""Effects: the actual things printed abilities do.

Every effect implements ``resolve(game, ctx)``.  ``ctx`` is a dict carrying the
resolution context: the controlling ``player``, the ``opponent``, the ``card``
that produced the effect, its in-play ``source`` (or None for actions), and for
some triggers an ``other`` character.

Effects ask questions through ``game.choose_*`` / ``game.confirm``, which route
to the controller of the deciding player.  Keeping choices synchronous means an
effect is an ordinary function, and a game state stays plain data that AI search
can deep-copy.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cards import RECKLESS

ANY = "any"
OWN = "own"
OPPOSING = "opposing"


@dataclass(frozen=True)
class Effect:
    def resolve(self, game, ctx):  # pragma: no cover - abstract
        raise NotImplementedError

    def __deepcopy__(self, memo):
        return self

    def __copy__(self):
        return self


@dataclass(frozen=True)
class Sequence(Effect):
    effects: tuple = ()

    def resolve(self, game, ctx):
        for effect in self.effects:
            effect.resolve(game, ctx)


# --------------------------------------------------------------------------
# Card flow
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DrawCards(Effect):
    count: int = 1

    def resolve(self, game, ctx):
        game.draw_cards(ctx["player"], self.count)


@dataclass(frozen=True)
class DrawThenDiscard(Effect):
    draw: int = 2
    discard: int = 2

    def resolve(self, game, ctx):
        player = ctx["player"]
        game.draw_cards(player, self.draw)
        for _ in range(self.discard):
            if not player.hand:
                return
            card = game.choose_card(player, "Discard a card", list(player.hand),
                                    intent="discard")
            if card is None:
                card = player.hand[0]
            player.hand.remove(card)
            player.discard.append(card)
            game.log(f"{player.name} discards {card.full_name}")


@dataclass(frozen=True)
class ReturnCharacterFromDiscardToHand(Effect):
    def resolve(self, game, ctx):
        player = ctx["player"]
        options = [c for c in player.discard if c.is_character]
        if not options:
            return
        card = game.choose_card(player, "Return a character card from your discard",
                                options, intent="revive")
        if card is None:
            return
        player.discard.remove(card)
        player.hand.append(card)
        game.log(f"{player.name} returns {card.full_name} to hand")


@dataclass(frozen=True)
class ShuffleCardFromAnyDiscardIntoDeck(Effect):
    optional: bool = True

    def resolve(self, game, ctx):
        player = ctx["player"]
        options = []
        for owner in game.players:
            options.extend((owner, card) for card in owner.discard)
        if not options:
            return
        choice = game.choose(player, "Shuffle a card from a discard pile into its deck",
                             options, kind="discard_card", intent="recycle",
                             optional=self.optional,
                             labeler=lambda o: f"{o[1].full_name} ({o[0].name}'s discard)")
        if choice is None:
            return
        owner, card = choice
        owner.discard.remove(card)
        owner.deck.append(card)
        game.shuffle_deck(owner)
        game.log(f"{player.name} shuffles {card.full_name} into {owner.name}'s deck")


@dataclass(frozen=True)
class ScryTopCard(Effect):
    """Look at the top card of your deck; put it on the top or the bottom."""

    def resolve(self, game, ctx):
        player = ctx["player"]
        if not player.deck:
            return
        card = player.deck[0]
        keep = game.choose(player, f"Top card is {card.full_name}",
                           [True, False], kind="scry", intent="scry",
                           labeler=lambda o: "Keep on top" if o else "Put on the bottom",
                           meta={"card": card})
        if keep is False:
            player.deck.pop(0)
            player.deck.append(card)
            game.log(f"{player.name} puts the top card on the bottom")
        else:
            game.log(f"{player.name} keeps the top card")


@dataclass(frozen=True)
class LookAtTopTakeOne(Effect):
    """Look at the top N cards, put one in hand, the rest on the bottom."""

    count: int = 2
    character_only: bool = False
    optional: bool = False

    def resolve(self, game, ctx):
        player = ctx["player"]
        seen = player.deck[: self.count]
        if not seen:
            return
        del player.deck[: len(seen)]
        options = [c for c in seen if not self.character_only or c.is_character]
        chosen = None
        if options:
            chosen = game.choose_card(player, "Put a card into your hand", options,
                                      intent="draw_pick", optional=self.optional)
        if chosen is not None:
            seen.remove(chosen)
            player.hand.append(chosen)
            game.log(f"{player.name} puts a card into their hand")
        player.deck.extend(seen)


@dataclass(frozen=True)
class PutTopCardIntoInkwell(Effect):
    optional: bool = False

    def resolve(self, game, ctx):
        player = ctx["player"]
        if not player.deck:
            return
        if self.optional and not game.confirm(
            player, "Put the top card of your deck into your inkwell?", intent="ink_top"
        ):
            return
        card = player.deck.pop(0)
        game.put_into_inkwell(player, card, ready=False)
        game.log(f"{player.name} puts the top card of their deck into their inkwell")


@dataclass(frozen=True)
class SelfToInkwell(Effect):
    """Gramma Tala: put this card into your inkwell facedown and exerted."""

    optional: bool = True

    def resolve(self, game, ctx):
        player = ctx["player"]
        card = ctx["card"]
        if card not in player.discard:
            return
        player.discard.remove(card)
        game.put_into_inkwell(player, card, ready=False)
        game.log(f"{player.name} puts {card.full_name} into their inkwell")


# --------------------------------------------------------------------------
# Lore
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class GainLore(Effect):
    amount: int = 1

    def resolve(self, game, ctx):
        game.gain_lore(ctx["player"], self.amount)


@dataclass(frozen=True)
class OpponentsLoseLore(Effect):
    amount: int = 1

    def resolve(self, game, ctx):
        game.lose_lore(ctx["opponent"], self.amount)


@dataclass(frozen=True)
class QuestDrainThisTurn(Effect):
    """Steal from the Rich: whenever one of your characters quests this turn,
    each opponent loses 1 lore."""

    amount: int = 1

    def resolve(self, game, ctx):
        ctx["player"].quest_drain += self.amount
        game.log(f"{ctx['player'].name}'s quests will drain lore this turn")


# --------------------------------------------------------------------------
# Damage / removal
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class DealDamage(Effect):
    amount: int = 1
    scope: str = ANY
    damaged_only: bool = False
    optional: bool = False

    def resolve(self, game, ctx):
        player = ctx["player"]
        predicate = (lambda ch: ch.damage > 0) if self.damaged_only else None
        target = game.choose_character(
            player,
            f"Deal {self.amount} damage to a character",
            scope=self.scope,
            intent="damage",
            optional=self.optional,
            predicate=predicate,
            meta={"amount": self.amount},
        )
        if target is None:
            return
        game.deal_damage(target, self.amount, source_player=player)


@dataclass(frozen=True)
class DealDamageToEachOpposing(Effect):
    amount: int = 2

    def resolve(self, game, ctx):
        for character in list(ctx["opponent"].characters):
            game.deal_damage(character, self.amount, source_player=ctx["player"])


@dataclass(frozen=True)
class BanishChosenCharacter(Effect):
    scope: str = ANY
    optional: bool = False

    def resolve(self, game, ctx):
        target = game.choose_character(ctx["player"], "Banish a character",
                                       scope=self.scope, intent="banish",
                                       optional=self.optional)
        if target is None:
            return
        game.banish_character(target)


@dataclass(frozen=True)
class BanishChosenItem(Effect):
    optional: bool = True

    def resolve(self, game, ctx):
        player = ctx["player"]
        options = game.targetable_items(player, ANY)
        if not options:
            return
        item = game.choose(player, "Banish an item", options, kind="item",
                           intent="banish_item", optional=self.optional)
        if item is None:
            return
        game.banish_item(item)


@dataclass(frozen=True)
class RemoveDamage(Effect):
    amount: int = 1
    scope: str = ANY
    trait: str = ""
    optional: bool = True

    def resolve(self, game, ctx):
        player = ctx["player"]
        predicate = None
        if self.trait:
            predicate = lambda ch: ch.card.has_trait(self.trait)  # noqa: E731
        target = game.choose_character(
            player, f"Remove up to {self.amount} damage from a character",
            scope=self.scope, intent="heal", optional=self.optional,
            predicate=predicate, meta={"amount": self.amount},
        )
        if target is None:
            return
        game.remove_damage(target, self.amount)


@dataclass(frozen=True)
class RemoveDamageFromEachOfYourCharacters(Effect):
    amount: int = 3

    def resolve(self, game, ctx):
        for character in ctx["player"].characters:
            game.remove_damage(character, self.amount)


@dataclass(frozen=True)
class ReturnChosenCharacterToHand(Effect):
    scope: str = ANY
    optional: bool = False

    def resolve(self, game, ctx):
        target = game.choose_character(ctx["player"], "Return a character to their hand",
                                       scope=self.scope, intent="return_hand",
                                       optional=self.optional)
        if target is None:
            return
        game.return_character_to_hand(target)


@dataclass(frozen=True)
class ReturnBanishedCardToHand(Effect):
    """Return the character banished by the triggering event to its owner's hand."""

    def resolve(self, game, ctx):
        other = ctx.get("other")
        if other is None:
            return
        owner = ctx["player"]
        card = other.card
        if card in owner.discard:
            owner.discard.remove(card)
            owner.hand.append(card)
            game.log(f"{owner.name} returns {card.full_name} to hand")


# --------------------------------------------------------------------------
# Stat and state modification
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ModifyStrength(Effect):
    amount: int = 2
    scope: str = ANY
    villain_amount: int = 0     # Vicious Betrayal
    name_bonus: tuple = ()      # (name, amount) - Stolen Scimitar
    optional: bool = False

    def resolve(self, game, ctx):
        player = ctx["player"]
        verb = "gets" if self.amount >= 0 else "gets"
        target = game.choose_character(
            player, f"Chosen character {verb} {self.amount:+d} strength this turn",
            scope=self.scope, intent="buff" if self.amount > 0 else "debuff",
            optional=self.optional, meta={"amount": self.amount},
        )
        if target is None:
            return
        amount = self.amount
        if self.villain_amount and target.card.has_trait("Villain"):
            amount = self.villain_amount
        if self.name_bonus and target.card.name == self.name_bonus[0]:
            amount = self.name_bonus[1]
        target.strength_mod += amount
        game.log(f"{target.card.full_name} gets {amount:+d} strength this turn")


@dataclass(frozen=True)
class ReadyChosenCharacter(Effect):
    scope: str = ANY
    cant_quest: bool = True
    optional: bool = False

    def resolve(self, game, ctx):
        player = ctx["player"]
        target = game.choose_character(player, "Ready a character", scope=self.scope,
                                       intent="ready", optional=self.optional,
                                       predicate=lambda ch: not ch.ready)
        if target is None:
            return
        target.ready = True
        if self.cant_quest:
            target.cant_quest = True
        game.log(f"{target.card.full_name} is readied"
                 + (" (can't quest this turn)" if self.cant_quest else ""))


@dataclass(frozen=True)
class ReadyOtherPrincesses(Effect):
    """Moana: ready your other Princess characters; they can't quest this turn."""

    def resolve(self, game, ctx):
        player = ctx["player"]
        source = ctx.get("source")
        readied = []
        for character in player.characters:
            if character is source:
                continue
            if character.card.has_trait("Princess"):
                character.ready = True
                character.cant_quest = True
                readied.append(character.card.name)
        if readied:
            game.log(f"{player.name} readies {', '.join(readied)} (they can't quest)")


@dataclass(frozen=True)
class SetFlagNextTurn(Effect):
    """Apply a restriction (or Reckless) during the target's next turn."""

    flag: str = "cant_quest"
    scope: str = ANY
    optional: bool = False

    def resolve(self, game, ctx):
        player = ctx["player"]
        prompts = {
            "cant_quest": "Chosen character can't quest during their next turn",
            "cant_challenge": "Chosen character can't challenge during their next turn",
            "reckless": "Chosen character gains Reckless during their next turn",
        }
        target = game.choose_character(player, prompts.get(self.flag, self.flag),
                                       scope=self.scope, intent=self.flag,
                                       optional=self.optional)
        if target is None:
            return
        target.pending_flags[self.flag] = True
        game.log(f"{target.card.full_name}: {prompts.get(self.flag, self.flag)}")


@dataclass(frozen=True)
class SupportEffect(Effect):
    """The Support keyword: add this character's strength to another character's."""

    def resolve(self, game, ctx):
        player = ctx["player"]
        source = ctx["source"]
        amount = game.strength_of(source)
        if amount <= 0:
            return
        target = game.choose_character(
            player, f"Add {amount} strength to another character",
            scope=OWN, intent="support", optional=True,
            exclude=(source,), meta={"amount": amount},
        )
        if target is None:
            return
        target.strength_mod += amount
        game.log(f"{source.card.name} supports {target.card.full_name} (+{amount})")


RECKLESS_FLAG = RECKLESS.lower()
