"""Controllers: the players behind the game engine.

* :class:`RandomController` – picks legal actions at random (a test baseline).
* :class:`HeuristicController` – a fast rule-based policy.  It is also the AI's
  opponent model during search, and it answers the small choices that come up
  inside effects ("which character do I damage?").
* :class:`HumanController` – a command line interface.
"""

from __future__ import annotations

import random

from .actions import (ActivateAction, ChallengeAction, InkAction, PassAction,
                      PlayAction, QuestAction, ShiftAction, SingAction)
from .cards import RECKLESS, format_keywords
from .effects import (DealDamage, ModifyStrength, ReadyChosenCharacter,
                      RemoveDamage, SetFlagNextTurn)
from .evaluate import DEFAULT_WEIGHTS, card_quality, character_value


class Controller:
    def __init__(self, name):
        self.name = name

    def choose_action(self, game, player, actions):  # pragma: no cover - abstract
        raise NotImplementedError

    def choose(self, game, player, prompt, options, kind, intent=None,
               optional=False, labeler=None, meta=None):  # pragma: no cover
        raise NotImplementedError


class RandomController(Controller):
    def __init__(self, name, seed=None):
        super().__init__(name)
        self.rng = random.Random(seed)

    def choose_action(self, game, player, actions):
        return self.rng.choice(actions)

    def choose(self, game, player, prompt, options, kind, intent=None,
               optional=False, labeler=None, meta=None):
        if kind == "confirm":
            return self.rng.choice(options)
        if optional and self.rng.random() < 0.2:
            return None
        return self.rng.choice(options)


class HeuristicController(Controller):
    """Rule-based policy: ink, develop the board, take good trades, then quest."""

    def __init__(self, name="heuristic", weights=DEFAULT_WEIGHTS):
        super().__init__(name)
        self.weights = weights

    def card_quality(self, card):
        return card_quality(card, self.weights)

    def character_value(self, game, character):
        return character_value(game, character, self.weights)

    # -- main phase ----------------------------------------------------

    def choose_action(self, game, player, actions):
        best, best_score = None, None
        for action in actions:
            score = self.score_action(game, player, action)
            if best_score is None or score > best_score:
                best, best_score = action, score
        return best

    def score_action(self, game, player, action):
        if isinstance(action, InkAction):
            if player.total_ink >= 9:
                return -1.0
            return 8.0 - 0.15 * self.card_quality(action.card)
        if isinstance(action, SingAction):
            return 6.0 + 0.1 * action.card.cost
        if isinstance(action, (PlayAction, ShiftAction)):
            return 4.5 + 0.2 * action.card.cost + 0.05 * self.card_quality(action.card)
        if isinstance(action, ChallengeAction):
            attacker = player.character_by_uid(action.uid)
            defender = game.other_player(player).character_by_uid(action.target_uid)
            if attacker is None or defender is None:
                return -5.0
            return 2.0 + self.challenge_value(game, attacker, defender)
        if isinstance(action, QuestAction):
            character = player.character_by_uid(action.uid)
            if character is None:
                return -5.0
            return 2.0 + self.weights.lore * character.card.lore * 0.8
        if isinstance(action, ActivateAction):
            return self.activation_score(game, player, action)
        if isinstance(action, PassAction):
            return 0.0
        return -10.0  # pragma: no cover

    def challenge_value(self, game, attacker, defender):
        attack = game.strength_of(attacker, challenging=True)
        defence = game.strength_of(defender)
        target_hp = game.remaining_willpower(defender)
        own_hp = game.remaining_willpower(attacker)
        kills = attack >= target_hp
        dies = defence >= own_hp
        value = 0.0
        target_value = self.character_value(game, defender)
        own_value = self.character_value(game, attacker)
        if kills:
            value += target_value
        elif target_hp > 0:
            value += 0.35 * target_value * min(1.0, attack / target_hp)
        if dies:
            value -= own_value
        elif own_hp > 0:
            value -= 0.20 * own_value * min(1.0, defence / own_hp)
        # A character that challenges cannot also quest this turn - unless it
        # was never going to be able to quest anyway.
        keywords = game.keywords_of(attacker)
        if not attacker.cant_quest and not keywords.get(RECKLESS):
            value -= 0.5 * self.weights.lore * attacker.card.lore
        return value

    def activation_score(self, game, player, action):
        source = (player.item_by_uid(action.uid) if action.is_item
                  else player.character_by_uid(action.uid))
        if source is None:
            return -5.0
        ability = game.activated_abilities(source.card)[action.ability_index]
        effect = ability.effect
        opponent = game.other_player(player)
        if isinstance(effect, RemoveDamage):
            best = 0
            for character in player.characters:
                if effect.trait and not character.card.has_trait(effect.trait):
                    continue
                best = max(best, min(effect.amount, character.damage))
            return 1.5 + 0.5 * best if best else -1.0
        if isinstance(effect, ReadyChosenCharacter):
            exerted = [c for c in player.characters if not c.ready and not c.drying]
            if not exerted or not opponent.characters:
                return -1.0
            return 1.8
        if isinstance(effect, ModifyStrength):
            ready = [c for c in player.characters if c.ready and not c.drying]
            if not ready or not any(not c.ready for c in opponent.characters):
                return -1.0
            return 1.6
        if isinstance(effect, SetFlagNextTurn):
            if not opponent.characters:
                return -1.0
            return 1.4
        if isinstance(effect, DealDamage):
            return 1.5 if opponent.characters else -1.0
        return -1.0

    # -- choices inside effects ----------------------------------------

    def choose(self, game, player, prompt, options, kind, intent=None,
               optional=False, labeler=None, meta=None):
        meta = meta or {}
        opponent = game.other_player(player)
        if kind == "confirm":
            return self.confirm_choice(game, player, intent, meta)
        if kind == "character":
            return self.choose_character(game, player, options, intent, optional, meta)
        if kind == "card":
            return self.choose_card(game, player, options, intent, optional, meta)
        if kind == "item":
            theirs = [i for i in options if i.owner_index == opponent.index]
            if theirs:
                return max(theirs, key=lambda i: i.card.cost)
            return None if optional else options[0]
        if kind == "discard_card":
            # Magic Broom: recycle your own best character, otherwise decline.
            mine = [(owner, card) for owner, card in options
                    if owner.index == player.index and card.is_character]
            if mine:
                return max(mine, key=lambda oc: self.card_quality(oc[1]))
            return None if optional else options[0]
        if kind == "scry":
            card = meta.get("card")
            keep = bool(card) and self.card_quality(card) >= 3.0
            return keep if keep in options else options[0]
        return None if optional else options[0]

    def confirm_choice(self, game, player, intent, meta):
        if intent == "go_first":
            return True
        if intent == "bodyguard_exert":
            # Enter exerted to soak a challenge only if the body survives the
            # opponent's biggest attacker.
            opponent = game.other_player(player)
            threats = [game.strength_of(c, challenging=True)
                       for c in opponent.characters if c.ready or c.drying]
            biggest = max(threats) if threats else 0
            card = meta.get("card")
            willpower = card.willpower if card else 0
            return bool(threats) and willpower > biggest
        return True

    def choose_character(self, game, player, options, intent, optional, meta):
        opponent = game.other_player(player)
        mine = [c for c in options if c.owner_index == player.index]
        theirs = [c for c in options if c.owner_index == opponent.index]
        amount = meta.get("amount", 0)

        if intent == "damage":
            if theirs:
                lethal = [c for c in theirs if game.remaining_willpower(c) <= amount]
                if lethal:
                    return max(lethal, key=lambda c: self.character_value(game, c))
                return max(theirs, key=lambda c: (self.character_value(game, c)
                                                  - game.remaining_willpower(c) * 0.3))
            return None if optional else (mine[0] if mine else None)
        if intent == "banish":
            if theirs:
                return max(theirs, key=lambda c: self.character_value(game, c))
            return None if optional else (mine[0] if mine else None)
        if intent == "return_hand":
            if theirs:
                return max(theirs, key=lambda c: self.character_value(game, c)
                           + 0.3 * c.card.cost)
            return None if optional else (mine[0] if mine else None)
        if intent == "debuff":
            if theirs:
                # Best case: the debuff means one of our attackers now survives
                # the challenge it wants to make.
                reduction = max(1, -amount)
                for attacker in mine:
                    if not attacker.ready or attacker.drying:
                        continue
                    own_hp = game.remaining_willpower(attacker)
                    for target in game.challenge_targets(attacker):
                        if target not in theirs:
                            continue
                        defence = game.strength_of(target)
                        if defence >= own_hp > defence - reduction:
                            return target
                return max(theirs, key=lambda c: game.strength_of(c))
            return None if optional else (mine[0] if mine else None)
        if intent in ("buff", "support"):
            ready = [c for c in mine if c.ready and not c.drying]
            pool = ready or mine
            if not pool:
                return None
            # Prefer a character the buff turns into a winning attacker.
            bonus = max(1, amount)
            enabled = []
            for character in ready:
                attack = game.strength_of(character, challenging=True)
                for target in game.challenge_targets(character):
                    hp = game.remaining_willpower(target)
                    if attack < hp <= attack + bonus:
                        enabled.append((self.character_value(game, target), character))
                        break
            if enabled:
                return max(enabled, key=lambda pair: pair[0])[1]
            return max(pool, key=lambda c: game.strength_of(c))
        if intent == "heal":
            damaged = [c for c in mine if c.damage > 0]
            if damaged:
                return max(damaged, key=lambda c: (min(amount, c.damage),
                                                   self.character_value(game, c)))
            return None if optional else (mine[0] if mine else None)
        if intent == "ready":
            pool = [c for c in mine if not c.ready]
            if pool:
                return max(pool, key=lambda c: self.character_value(game, c))
            return None if optional else (options[0] if options else None)
        if intent == "cant_quest":
            if theirs:
                return max(theirs, key=lambda c: (c.card.lore,
                                                  self.character_value(game, c)))
            return None if optional else (mine[0] if mine else None)
        if intent == "cant_challenge":
            if theirs:
                return max(theirs, key=lambda c: game.strength_of(c, challenging=True))
            return None if optional else (mine[0] if mine else None)
        if intent == "reckless":
            if theirs:
                return max(theirs, key=lambda c: (c.card.lore,
                                                  -game.strength_of(c)))
            return None if optional else (mine[0] if mine else None)
        if theirs:
            return theirs[0]
        return None if optional else options[0]

    def choose_card(self, game, player, options, intent, optional, meta):
        if intent == "discard":
            return min(options, key=lambda c: (self.card_quality(c)
                                               - 0.3 * min(c.cost, 6)))
        if intent in ("revive", "draw_pick"):
            return max(options, key=self.card_quality)
        if intent == "alter_hand":
            return self.alter_hand_choice(options, meta)
        return None if optional else options[0]

    def alter_hand_choice(self, hand, meta):
        """Keep a playable curve: bottom expensive or uninkable excess."""
        if meta.get("put_back", 0) >= 4:
            return None
        cheap = [c for c in hand if c.cost <= 3]
        expensive = sorted((c for c in hand if c.cost >= 5), key=lambda c: -c.cost)
        inkable = [c for c in hand if c.inkable]
        if len(inkable) < 3:
            uninkable = sorted((c for c in hand if not c.inkable),
                               key=lambda c: -c.cost)
            if uninkable:
                return uninkable[0]
        if expensive and len(cheap) < 3:
            return expensive[0]
        if len(expensive) > 2:
            return expensive[0]
        return None


# --------------------------------------------------------------------------
# Human interface
# --------------------------------------------------------------------------


def _character_line(game, character, prefix=""):
    keywords = format_keywords(game.keywords_of(character))
    state = []
    if not character.ready:
        state.append("exerted")
    if character.drying:
        state.append("drying")
    if character.cant_quest:
        state.append("can't quest")
    if character.cant_challenge:
        state.append("can't challenge")
    if character.pending_flags:
        state.append("next turn: " + ", ".join(character.pending_flags))
    bits = [f"{prefix}{character.card.full_name}",
            f"{game.strength_of(character)} strength",
            f"{game.remaining_willpower(character)}/{character.card.willpower} "
            f"willpower",
            f"{character.card.lore} lore"]
    if keywords:
        bits.append(keywords)
    if state:
        bits.append("[" + ", ".join(state) + "]")
    return "  " + " | ".join(bits)


def render_board(game, viewpoint):
    me = game.players[viewpoint]
    them = game.players[1 - viewpoint]
    lines = []
    lines.append("=" * 72)
    lines.append(f"{them.name}: {them.lore} lore | hand {len(them.hand)} | "
                 f"ink {them.available_ink}/{them.total_ink} | "
                 f"deck {len(them.deck)} | discard {len(them.discard)}")
    if them.characters:
        for character in them.characters:
            lines.append(_character_line(game, character))
    else:
        lines.append("  (no characters)")
    if them.items:
        lines.append("  items: " + ", ".join(
            i.card.name + ("" if i.ready else " (exerted)") for i in them.items))
    lines.append("-" * 72)
    if me.characters:
        for character in me.characters:
            lines.append(_character_line(game, character))
    else:
        lines.append("  (no characters)")
    if me.items:
        lines.append("  items: " + ", ".join(
            i.card.name + ("" if i.ready else " (exerted)") for i in me.items))
    lines.append(f"{me.name}: {me.lore} lore | ink {me.available_ink}/{me.total_ink} | "
                 f"deck {len(me.deck)} | discard {len(me.discard)}")
    lines.append("Your hand:")
    for index, card in enumerate(me.hand, 1):
        lines.append(f"  {index}. {card.describe()}")
    lines.append("=" * 72)
    return "\n".join(lines)


class HumanController(Controller):
    def __init__(self, name="You", input_fn=input, output_fn=print):
        super().__init__(name)
        self.input_fn = input_fn
        self.output_fn = output_fn

    def _prompt_index(self, count, allow_none=False, extra=""):
        while True:
            raw = self.input_fn(f"Choice [1-{count}]{extra}: ").strip().lower()
            if raw in ("?", "h", "help"):
                self.output_fn("Enter the number of the option you want.")
                continue
            if allow_none and raw in ("", "0", "s", "skip", "n", "none"):
                return None
            try:
                value = int(raw)
            except ValueError:
                self.output_fn("Please enter a number.")
                continue
            if 1 <= value <= count:
                return value - 1
            self.output_fn("Out of range.")

    def choose_action(self, game, player, actions):
        self.output_fn(render_board(game, player.index))
        self.output_fn("Your options:")
        ordered = sorted(actions, key=_action_sort_key)
        for index, action in enumerate(ordered, 1):
            self.output_fn(f"  {index}. {action.describe(game)}")
        index = self._prompt_index(len(ordered))
        return ordered[index]

    def choose(self, game, player, prompt, options, kind, intent=None,
               optional=False, labeler=None, meta=None):
        self.output_fn("")
        self.output_fn(prompt)
        for index, option in enumerate(options, 1):
            label = labeler(option) if labeler else str(option)
            self.output_fn(f"  {index}. {label}")
        extra = " or 0 to skip" if optional else ""
        index = self._prompt_index(len(options), allow_none=optional, extra=extra)
        if index is None:
            return None
        return options[index]


_ACTION_ORDER = {InkAction: 0, PlayAction: 1, ShiftAction: 2, SingAction: 3,
                 ActivateAction: 4, QuestAction: 5, ChallengeAction: 6,
                 PassAction: 9}


def _action_sort_key(action):
    order = _ACTION_ORDER.get(type(action), 8)
    cost = getattr(getattr(action, "card", None), "cost", 0)
    name = getattr(getattr(action, "card", None), "name", "")
    return (order, cost, name, getattr(action, "uid", 0))
