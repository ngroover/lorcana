"""The Lorcana rules engine.

The game is driven by controllers: :meth:`Game.main_phase` repeatedly asks the
current player's controller to pick one of the legal actions, applies it, and
loops.  Choices that arise *inside* an action (which character to damage, whether
to use a "you may" trigger) are asked synchronously through ``Game.choose*``.

Because every choice is a synchronous callback and the state is plain data, a
game can be deep-copied mid-turn, which is what the search AI in ``ai.py`` uses
to look ahead.
"""

from __future__ import annotations

import copy
import random

from .abilities import ActivatedAbility, Event, StaticAbility, TriggeredAbility
from .actions import (ActivateAction, ChallengeAction, InkAction, PassAction,
                      PlayAction, QuestAction, ShiftAction, SingAction)
from .cards import (BODYGUARD, CHALLENGER, EVASIVE, RECKLESS, RUSH, SHIFT,
                    SINGER, SUPPORT, WARD)
from .effects import ANY, OPPOSING, OWN, SupportEffect
from .state import InkCard, InPlayCharacter, InPlayItem, PlayerState

WINNING_LORE = 20
STARTING_HAND = 7
MAX_TURNS = 400

# Most cards have no static abilities; caching the lookup keeps the hot path
# (querying keywords and costs) cheap during AI search.
_STATIC_CACHE = {}


def _statics_of(card):
    statics = _STATIC_CACHE.get(card.id)
    if statics is None:
        statics = tuple(a for a in card.abilities if isinstance(a, StaticAbility))
        _STATIC_CACHE[card.id] = statics
    return statics


class Game:
    """A single game of Lorcana between two players."""

    #: attributes that are shared, not copied, when cloning for search
    _SHARED_ATTRS = ("controllers", "verbose", "log_sink")

    def __init__(self, contestants, seed=None, verbose=False, log_sink=None):
        """``contestants`` is a sequence of two ``(name, decklist, controller)``."""
        self._seed_base = seed if seed is not None else random.randrange(1 << 30)
        self._clone_counter = 0
        self.rng = random.Random(seed)
        self.players = []
        self.controllers = []
        for index, (name, decklist, controller) in enumerate(contestants):
            self.players.append(PlayerState(index=index, name=name,
                                            deck=list(decklist.cards)))
            self.controllers.append(controller)
        self.current_index = 0
        self.first_player_index = 0
        self.turn_number = 0
        self.winner = None
        self.verbose = verbose
        self.log_sink = log_sink
        self._next_uid = 1
        self._support_effect = SupportEffect()

    # ------------------------------------------------------------------
    # basics
    # ------------------------------------------------------------------

    @property
    def current_player(self):
        return self.players[self.current_index]

    @property
    def opponent_player(self):
        return self.players[1 - self.current_index]

    def other_player(self, player):
        return self.players[1 - player.index]

    def controller_for(self, player):
        return self.controllers[player.index]

    def owner_of(self, in_play):
        return self.players[in_play.owner_index]

    def log(self, message):
        if self.log_sink is not None:
            self.log_sink(message)
        elif self.verbose:
            print(message)

    def new_uid(self):
        uid = self._next_uid
        self._next_uid += 1
        return uid

    def __deepcopy__(self, memo):
        clone = Game.__new__(Game)
        memo[id(self)] = clone
        for key, value in self.__dict__.items():
            if key in self._SHARED_ATTRS:
                clone.__dict__[key] = list(value) if key == "controllers" else value
            else:
                clone.__dict__[key] = copy.deepcopy(value, memo)
        return clone

    def clone(self, controllers=None, quiet=True):
        """Copy the game.  Controllers are replaced, never copied."""
        clone = copy.deepcopy(self)
        if controllers is not None:
            clone.controllers = list(controllers)
        if quiet:
            clone.verbose = False
            clone.log_sink = None
        return clone

    def fast_clone(self, controllers=None):
        """Copy the game the cheap way.  Used heavily by AI search.

        Only mutable game state is duplicated; cards, abilities and effects are
        immutable and shared.  The clone gets its own deterministic RNG so that
        searching never disturbs the real game's shuffles.
        """
        clone = Game.__new__(Game)
        clone.players = [player.copy() for player in self.players]
        clone.controllers = list(controllers) if controllers is not None \
            else list(self.controllers)
        clone.current_index = self.current_index
        clone.first_player_index = self.first_player_index
        clone.turn_number = self.turn_number
        clone.winner = self.winner
        clone.verbose = False
        clone.log_sink = None
        clone._next_uid = self._next_uid
        clone._support_effect = self._support_effect
        self._clone_counter += 1
        clone._clone_counter = 0
        clone._seed_base = self._seed_base
        clone.rng = random.Random(self._seed_base + self._clone_counter * 7919)
        return clone

    def clone_for_search(self, perspective, controllers=None):
        """Clone hiding information ``perspective`` should not know.

        The opponent's hand is replaced with a random sample of the cards they
        could be holding, and both decks are reshuffled, so search cannot peek at
        future draws or the opponent's grip.
        """
        clone = self.clone(controllers=controllers)
        clone.resample_hidden(perspective)
        return clone

    def resample_hidden(self, perspective):
        """Re-randomise everything ``perspective`` cannot see, in place."""
        me = self.players[perspective]
        them = self.players[1 - perspective]
        unseen = them.deck + them.hand
        self.rng.shuffle(unseen)
        hand_size = len(them.hand)
        them.hand = unseen[:hand_size]
        them.deck = unseen[hand_size:]
        self.rng.shuffle(me.deck)

    # ------------------------------------------------------------------
    # querying card properties (static abilities are resolved live)
    # ------------------------------------------------------------------

    def _static_abilities(self):
        for player in self.players:
            for source in player.characters:
                for ability in _statics_of(source.card):
                    yield player, source, ability
            for source in player.items:
                for ability in _statics_of(source.card):
                    yield player, source, ability

    def keywords_of(self, character):
        keywords = dict(character.card.keywords)
        for name, value in character.extra_keywords.items():
            if isinstance(value, int) and not isinstance(value, bool):
                keywords[name] = max(keywords.get(name, 0), value)
            else:
                keywords[name] = value
        for _player, source, ability in self._static_abilities():
            granted = ability.grant_keywords(self, source, character)
            if granted:
                for name, value in granted.items():
                    if isinstance(value, int) and not isinstance(value, bool):
                        keywords[name] = max(keywords.get(name, 0), value)
                    else:
                        keywords[name] = value
        return keywords

    def has_keyword(self, character, keyword):
        return bool(self.keywords_of(character).get(keyword))

    def strength_of(self, character, challenging=False):
        strength = character.card.strength + character.strength_mod
        if challenging:
            strength += self.keywords_of(character).get(CHALLENGER, 0)
        return max(0, strength)

    def remaining_willpower(self, character):
        return character.card.willpower - character.damage

    def effective_cost(self, player, card):
        cost = card.cost
        for owner, source, ability in self._static_abilities():
            if owner is player:
                cost += ability.cost_modifier(self, source, player, card)
        return max(0, cost)

    def activated_abilities(self, card):
        return [a for a in card.abilities if isinstance(a, ActivatedAbility)]

    def can_sing(self, singer, song):
        if not singer.ready or singer.drying:
            return False
        for _owner, source, ability in self._static_abilities():
            if ability.forbids_singing(self, source, singer):
                return False
        keywords = self.keywords_of(singer)
        value = max(singer.card.cost, keywords.get(SINGER, 0))
        return value >= song.cost

    # ------------------------------------------------------------------
    # asking questions
    # ------------------------------------------------------------------

    def choose(self, player, prompt, options, kind, intent=None, optional=False,
               labeler=None, meta=None):
        options = list(options)
        if not options:
            return None
        if len(options) == 1 and not optional:
            return options[0]
        controller = self.controller_for(player)
        choice = controller.choose(self, player, prompt, options, kind=kind,
                                   intent=intent, optional=optional,
                                   labeler=labeler, meta=meta or {})
        if choice is not None and choice not in options:
            raise ValueError(f"controller returned an illegal choice: {choice!r}")
        return choice

    def confirm(self, player, prompt, intent=None, meta=None):
        choice = self.choose(player, prompt, [True, False], kind="confirm",
                             intent=intent, meta=meta,
                             labeler=lambda o: "Yes" if o else "No")
        return bool(choice)

    def choose_card(self, player, prompt, cards, intent=None, optional=False):
        return self.choose(player, prompt, cards, kind="card", intent=intent,
                           optional=optional, labeler=lambda c: c.full_name)

    def targetable_characters(self, chooser, scope=ANY, for_challenge=False):
        """Characters ``chooser`` may choose.  Ward protects from opponents."""
        result = []
        if scope in (ANY, OWN):
            result.extend(chooser.characters)
        if scope in (ANY, OPPOSING):
            for character in self.other_player(chooser).characters:
                if for_challenge or not self.has_keyword(character, WARD):
                    result.append(character)
        return result

    def targetable_items(self, chooser, scope=ANY):
        result = []
        if scope in (ANY, OWN):
            result.extend(chooser.items)
        if scope in (ANY, OPPOSING):
            result.extend(self.other_player(chooser).items)
        return result

    def choose_character(self, player, prompt, scope=ANY, intent=None, optional=False,
                         predicate=None, exclude=(), meta=None):
        candidates = self.targetable_characters(player, scope)
        if predicate is not None:
            candidates = [c for c in candidates if predicate(c)]
        if exclude:
            candidates = [c for c in candidates if c not in exclude]
        return self.choose(player, prompt, candidates, kind="character",
                           intent=intent, optional=optional, meta=meta,
                           labeler=self.describe_character)

    def describe_character(self, character):
        owner = self.owner_of(character)
        keywords = self.keywords_of(character)
        from .cards import format_keywords
        bits = [character.card.full_name,
                f"{self.strength_of(character)}/{self.remaining_willpower(character)}",
                f"{character.card.lore}L"]
        if not character.ready:
            bits.append("exerted")
        if character.drying:
            bits.append("drying")
        keyword_text = format_keywords(keywords)
        if keyword_text:
            bits.append(keyword_text)
        who = owner.name if owner else "?"
        return f"{who}: " + " ".join(bits[:1]) + " (" + ", ".join(bits[1:]) + ")"

    # ------------------------------------------------------------------
    # game set-up
    # ------------------------------------------------------------------

    def shuffle_deck(self, player):
        self.rng.shuffle(player.deck)

    def setup(self):
        for player in self.players:
            self.shuffle_deck(player)
            self.draw_cards(player, STARTING_HAND, silent=True)
        roll_winner = self.rng.randrange(2)
        controller = self.controllers[roll_winner]
        go_first = controller.choose(
            self, self.players[roll_winner],
            "You won the die roll. Go first?", [True, False], kind="confirm",
            intent="go_first", optional=False,
            labeler=lambda o: "Go first" if o else "Go second", meta={})
        self.first_player_index = roll_winner if go_first else 1 - roll_winner
        self.current_index = self.first_player_index
        self.log(f"{self.players[self.first_player_index].name} goes first")
        for offset in range(2):
            self.alter_hand(self.players[(self.first_player_index + offset) % 2])
        self.turn_number = 1

    def alter_hand(self, player):
        """Once per game: put any number of cards on the bottom and redraw."""
        put_back = []
        while player.hand:
            card = self.choose(player,
                               f"Alter hand: put a card on the bottom? "
                               f"({len(put_back)} so far)",
                               list(player.hand), kind="card", intent="alter_hand",
                               optional=True, labeler=lambda c: c.full_name,
                               meta={"put_back": len(put_back)})
            if card is None:
                break
            player.hand.remove(card)
            put_back.append(card)
        if not put_back:
            return
        player.deck.extend(put_back)
        self.shuffle_deck(player)
        self.draw_cards(player, len(put_back), silent=True)
        self.log(f"{player.name} alters {len(put_back)} card(s)")

    # ------------------------------------------------------------------
    # turn structure
    # ------------------------------------------------------------------

    def run(self):
        self.setup()
        while self.winner is None and self.turn_number <= MAX_TURNS:
            self.play_turn()
            if self.winner is not None:
                break
            self.advance_turn()
        if self.winner is None:  # pragma: no cover - safety valve
            lore = [p.lore for p in self.players]
            self.winner = 0 if lore[0] >= lore[1] else 1
        self.log(f"{self.players[self.winner].name} wins "
                 f"({self.players[0].lore}-{self.players[1].lore})")
        return self.winner

    def play_turn(self):
        self.begin_turn()
        if self.winner is not None:
            return
        self.main_phase()
        self.end_turn()

    def advance_turn(self):
        self.current_index = 1 - self.current_index
        self.turn_number += 1

    def begin_turn(self):
        player = self.current_player
        self.log(f"--- Turn {self.turn_number}: {player.name} "
                 f"(lore {self.players[0].lore}-{self.players[1].lore}) ---")
        for character in player.characters:
            character.ready = True
            character.drying = False
            flags = character.pending_flags
            character.pending_flags = {}
            if flags.get("cant_quest"):
                character.cant_quest = True
            if flags.get("cant_challenge"):
                character.cant_challenge = True
            if flags.get("reckless"):
                character.extra_keywords[RECKLESS] = True
        for item in player.items:
            item.ready = True
        for ink in player.inkwell:
            ink.ready = True
        player.inked_this_turn = False
        player.quest_drain = 0
        # Draw step: the player who goes first skips it on the first turn.
        if not (self.turn_number == 1 and player.index == self.first_player_index):
            if not player.deck:
                player.lost_to_empty_deck = True
                self.winner = 1 - player.index
                self.log(f"{player.name} cannot draw and loses the game")
                return
            self.draw_cards(player, 1)

    def end_turn(self):
        for player in self.players:
            for character in player.characters:
                character.strength_mod = 0
                character.cant_quest = False
                character.cant_challenge = False
                character.extra_keywords = {}
        self.current_player.quest_drain = 0

    def main_phase(self):
        player = self.current_player
        controller = self.controller_for(player)
        guard = 0
        while self.winner is None:
            guard += 1
            if guard > 200:  # pragma: no cover - safety valve
                break
            actions = self.legal_actions()
            if not actions:
                break
            if len(actions) == 1:
                action = actions[0]
            else:
                action = controller.choose_action(self, player, actions)
                if action not in actions:
                    raise ValueError(f"illegal action from controller: {action!r}")
            if isinstance(action, PassAction):
                self.log(f"{player.name} passes")
                break
            self.apply(action)

    # ------------------------------------------------------------------
    # legal actions
    # ------------------------------------------------------------------

    def legal_actions(self):
        player = self.current_player
        actions = []
        if not player.inked_this_turn:
            for card in dict.fromkeys(c for c in player.hand if c.inkable):
                actions.append(InkAction(card))

        ink = player.available_ink
        for card in dict.fromkeys(player.hand):
            if self.effective_cost(player, card) <= ink:
                actions.append(PlayAction(card))
            shift_cost = card.keywords.get(SHIFT)
            if shift_cost is not None and shift_cost <= ink:
                for target in self._dedupe_characters(
                    c for c in player.characters if c.card.name == card.name
                ):
                    actions.append(ShiftAction(card, target.uid))
            if card.is_song:
                for singer in self._dedupe_characters(
                    c for c in player.characters if self.can_sing(c, card)
                ):
                    actions.append(SingAction(card, singer.uid))

        must_challenge = False
        for character in self._dedupe_characters(player.characters):
            keywords = self.keywords_of(character)
            active = character.ready and (not character.drying or keywords.get(RUSH))
            if character.ready and not character.drying and not character.cant_quest \
                    and not keywords.get(RECKLESS):
                actions.append(QuestAction(character.uid))
            if active and not character.cant_challenge:
                targets = self.challenge_targets(character)
                if targets and keywords.get(RECKLESS):
                    must_challenge = True
                for target in targets:
                    actions.append(ChallengeAction(character.uid, target.uid))
            if character.ready and not character.drying:
                actions.extend(self._activation_actions(player, character, is_item=False))
        for item in self._dedupe_items(player.items):
            actions.extend(self._activation_actions(player, item, is_item=True))

        if not must_challenge:
            actions.append(PassAction())
        return actions

    def _activation_actions(self, player, source, is_item):
        result = []
        for index, ability in enumerate(self.activated_abilities(source.card)):
            if ability.exert and not ability.banish_self and not source.ready:
                continue
            if ability.ink_cost > player.available_ink:
                continue
            result.append(ActivateAction(source.uid, index, is_item))
        return result

    def _character_key(self, character):
        return (character.card.id, character.ready, character.drying, character.damage,
                character.strength_mod, character.cant_quest, character.cant_challenge,
                tuple(sorted(character.extra_keywords.items())),
                tuple(sorted(character.pending_flags.items())))

    def _dedupe_characters(self, characters):
        """Collapse interchangeable copies so menus and search stay small."""
        seen = {}
        for character in characters:
            seen.setdefault(self._character_key(character), character)
        return list(seen.values())

    def _dedupe_items(self, items):
        seen = {}
        for item in items:
            seen.setdefault((item.card.id, item.ready), item)
        return list(seen.values())

    def challenge_targets(self, challenger):
        """Exerted opposing characters this character may legally challenge."""
        opponent = self.other_player(self.owner_of(challenger) or self.current_player)
        exerted = [c for c in opponent.characters if not c.ready]
        if not exerted:
            return []
        attacker_evasive = self.has_keyword(challenger, EVASIVE)
        legal = [c for c in exerted
                 if attacker_evasive or not self.has_keyword(c, EVASIVE)]
        bodyguards = [c for c in legal if self.has_keyword(c, BODYGUARD)]
        if bodyguards:
            legal = bodyguards
        return self._dedupe_characters(legal)

    # ------------------------------------------------------------------
    # applying actions
    # ------------------------------------------------------------------

    def apply(self, action):
        player = self.current_player
        if isinstance(action, InkAction):
            player.hand.remove(action.card)
            self.put_into_inkwell(player, action.card, ready=True)
            player.inked_this_turn = True
            self.log(f"{player.name} inks {action.card.full_name}")
        elif isinstance(action, PlayAction):
            self.play_card(player, action.card)
        elif isinstance(action, ShiftAction):
            target = player.character_by_uid(action.target_uid)
            self.play_card(player, action.card, shift_target=target)
        elif isinstance(action, SingAction):
            singer = player.character_by_uid(action.singer_uid)
            self.sing_song(player, action.card, singer)
        elif isinstance(action, QuestAction):
            self.do_quest(player.character_by_uid(action.uid))
        elif isinstance(action, ChallengeAction):
            attacker = player.character_by_uid(action.uid)
            defender = self.other_player(player).character_by_uid(action.target_uid)
            self.do_challenge(attacker, defender)
        elif isinstance(action, ActivateAction):
            source = (player.item_by_uid(action.uid) if action.is_item
                      else player.character_by_uid(action.uid))
            self.activate_ability(player, source, action.ability_index)
        elif isinstance(action, PassAction):
            pass
        else:  # pragma: no cover
            raise ValueError(f"unknown action {action!r}")

    def put_into_inkwell(self, player, card, ready=True):
        player.inkwell.append(InkCard(card, ready=ready))

    # -- playing cards --------------------------------------------------

    def play_card(self, player, card, shift_target=None):
        if shift_target is not None:
            cost = card.keywords.get(SHIFT, card.cost)
        else:
            cost = self.effective_cost(player, card)
        if cost > player.available_ink:
            raise ValueError(f"not enough ink to play {card.full_name}")
        player.hand.remove(card)
        player.exert_ink(cost)
        self.log(f"{player.name} plays {card.full_name}"
                 + (f" (shift onto {shift_target.card.full_name})" if shift_target else ""))

        if card.is_character:
            if shift_target is not None:
                shift_target.underneath.append(shift_target.card)
                shift_target.card = card
                character = shift_target
            else:
                character = InPlayCharacter(card=card, uid=self.new_uid(),
                                            owner_index=player.index)
                if card.keywords.get(BODYGUARD) and self.confirm(
                    player, f"Have {card.full_name} enter play exerted (Bodyguard)?",
                    intent="bodyguard_exert", meta={"card": card},
                ):
                    character.ready = False
                player.characters.append(character)
            self.fire_self_triggers(character, Event.ON_PLAY, player)
            self.fire_watcher_triggers(player, Event.YOU_PLAY_CHARACTER,
                                       other=character)
        elif card.is_item:
            item = InPlayItem(card=card, uid=self.new_uid(), owner_index=player.index)
            player.items.append(item)
            self.fire_triggers_for(player, item, card, Event.ON_PLAY)
        else:  # action / song
            self.resolve_card_effects(player, card)
            player.discard.append(card)
        self.check_win()

    def sing_song(self, player, song, singer):
        if not self.can_sing(singer, song):
            raise ValueError(f"{singer.card.full_name} cannot sing {song.full_name}")
        singer.ready = False
        player.hand.remove(song)
        self.log(f"{player.name} sings {song.full_name} with {singer.card.full_name}")
        self.resolve_card_effects(player, song)
        player.discard.append(song)
        self.check_win()

    def resolve_card_effects(self, player, card):
        for ability in card.abilities:
            if isinstance(ability, TriggeredAbility) and ability.event == Event.ON_PLAY:
                self.resolve_ability(ability, player, source=None, card=card)

    # -- questing and challenging ---------------------------------------

    def do_quest(self, character):
        player = self.owner_of(character)
        character.ready = False
        self.gain_lore(player, character.card.lore)
        if player.quest_drain:
            self.lose_lore(self.other_player(player), player.quest_drain)
        self.log(f"{player.name} quests with {character.card.full_name} "
                 f"(+{character.card.lore}, total {player.lore})")
        self.fire_self_triggers(character, Event.ON_QUEST, player)
        if self.has_keyword(character, SUPPORT):
            self.resolve_effect(self._support_effect, player, source=character,
                                card=character.card)
        self.check_win()

    def do_challenge(self, attacker, defender):
        attacker_owner = self.owner_of(attacker)
        defender_owner = self.owner_of(defender)
        attacker.ready = False
        self.log(f"{attacker_owner.name}'s {attacker.card.full_name} challenges "
                 f"{defender.card.full_name}")
        self.fire_self_triggers(defender, Event.CHALLENGED, defender_owner,
                               other=attacker)
        attack_power = self.strength_of(attacker, challenging=True)
        defence_power = self.strength_of(defender)
        # Damage is dealt simultaneously, so resolve banishment afterwards.
        self.deal_damage(defender, attack_power, source_player=attacker_owner,
                         check_banish=False)
        self.deal_damage(attacker, defence_power, source_player=defender_owner,
                         check_banish=False)
        defender_banished = self.remaining_willpower(defender) <= 0
        attacker_banished = self.remaining_willpower(attacker) <= 0
        # Both characters leave play together, before any trigger resolves: a
        # trigger must not be able to save a character that is already banished.
        if defender_banished:
            self.remove_from_play(defender)
        if attacker_banished:
            self.remove_from_play(attacker)
        if defender_banished:
            self.banish_triggers(defender, in_challenge=True, was_challenged=True)
        if attacker_banished:
            self.banish_triggers(attacker, in_challenge=True)
        if defender_banished:
            self.fire_self_triggers(attacker, Event.BANISHES_IN_CHALLENGE,
                                    attacker_owner, other=defender)
        if attacker_banished:
            self.fire_self_triggers(defender, Event.BANISHES_IN_CHALLENGE,
                                    defender_owner, other=attacker)
        self.check_win()

    # -- activated abilities --------------------------------------------

    def activate_ability(self, player, source, ability_index):
        ability = self.activated_abilities(source.card)[ability_index]
        if ability.ink_cost:
            player.exert_ink(ability.ink_cost)
        self.log(f"{player.name} activates {source.card.full_name}: {ability.text}")
        if ability.banish_self:
            self.banish_item(source)
        elif ability.exert:
            source.ready = False
        self.resolve_effect(ability.effect, player, source=source, card=source.card)
        self.check_win()

    # ------------------------------------------------------------------
    # primitive state changes
    # ------------------------------------------------------------------

    def draw_cards(self, player, count=1, silent=False):
        drawn = []
        for _ in range(count):
            if not player.deck:
                break
            drawn.append(player.deck.pop(0))
        player.hand.extend(drawn)
        if drawn and not silent:
            self.log(f"{player.name} draws {len(drawn)} card(s)")
        return drawn

    def gain_lore(self, player, amount):
        if amount <= 0:
            return
        player.lore += amount
        self.check_win()

    def lose_lore(self, player, amount):
        if amount <= 0:
            return
        player.lore = max(0, player.lore - amount)
        self.log(f"{player.name} loses {amount} lore (now {player.lore})")

    def check_win(self):
        if self.winner is not None:
            return
        for player in self.players:
            if player.lore >= WINNING_LORE:
                self.winner = player.index
                self.log(f"{player.name} reaches {player.lore} lore")

    def deal_damage(self, character, amount, source_player=None, check_banish=True):
        if amount <= 0:
            return
        character.damage += amount
        self.log(f"{character.card.full_name} takes {amount} damage "
                 f"({self.remaining_willpower(character)} willpower left)")
        if check_banish and self.remaining_willpower(character) <= 0:
            self.banish_character(character)

    def remove_damage(self, character, amount):
        healed = min(amount, character.damage)
        if healed <= 0:
            return
        character.damage -= healed
        self.log(f"{character.card.full_name} heals {healed} damage")

    def remove_from_play(self, character):
        """Move a banished character (and anything under it) to the discard."""
        owner = self.owner_of(character)
        if character not in owner.characters:
            return False
        owner.characters.remove(character)
        owner.discard.append(character.card)
        owner.discard.extend(character.underneath)
        character.underneath = []
        self.log(f"{owner.name}'s {character.card.full_name} is banished")
        return True

    def banish_triggers(self, character, in_challenge=False, was_challenged=False):
        owner = self.owner_of(character)
        self.fire_self_triggers(character, Event.ON_BANISHED, owner)
        if was_challenged:
            self.fire_self_triggers(character, Event.CHALLENGED_AND_BANISHED, owner)
        if in_challenge:
            self.fire_watcher_triggers(owner, Event.OTHER_BANISHED_IN_CHALLENGE,
                                       other=character, exclude=character)

    def banish_character(self, character, in_challenge=False, was_challenged=False):
        if not self.remove_from_play(character):
            return
        self.banish_triggers(character, in_challenge=in_challenge,
                             was_challenged=was_challenged)

    def banish_item(self, item):
        owner = self.owner_of(item)
        if item not in owner.items:
            return
        owner.items.remove(item)
        owner.discard.append(item.card)
        self.log(f"{owner.name}'s {item.card.full_name} is banished")

    def return_character_to_hand(self, character):
        owner = self.owner_of(character)
        if character not in owner.characters:
            return
        owner.characters.remove(character)
        owner.hand.append(character.card)
        owner.discard.extend(character.underneath)
        character.underneath = []
        self.log(f"{character.card.full_name} returns to {owner.name}'s hand")

    # ------------------------------------------------------------------
    # triggers
    # ------------------------------------------------------------------

    def fire_self_triggers(self, source, event, owner, other=None):
        self.fire_triggers_for(owner, source, source.card, event, other=other)

    def fire_triggers_for(self, owner, source, card, event, other=None):
        for ability in card.abilities:
            if isinstance(ability, TriggeredAbility) and ability.event == event:
                self.resolve_ability(ability, owner, source=source, card=card,
                                     other=other)

    def fire_watcher_triggers(self, owner, event, other=None, exclude=None):
        sources = [s for s in list(owner.characters) + list(owner.items)
                   if s is not exclude]
        for source in sources:
            self.fire_triggers_for(owner, source, source.card, event, other=other)

    def resolve_ability(self, ability, owner, source=None, card=None, other=None):
        ctx = {"game": self, "player": owner, "opponent": self.other_player(owner),
               "source": source, "card": card, "other": other}
        if not ability.matches(self, ctx):
            return
        if ability.effect is None:
            return
        if ability.optional:
            prompt = ability.text or "Use ability?"
            if not self.confirm(owner, prompt, intent="trigger"):
                return
        if ability.text:
            self.log(f"{owner.name}: {ability.text}")
        ability.effect.resolve(self, ctx)

    def resolve_effect(self, effect, owner, source=None, card=None, other=None):
        ctx = {"game": self, "player": owner, "opponent": self.other_player(owner),
               "source": source, "card": card, "other": other}
        effect.resolve(self, ctx)

    # ------------------------------------------------------------------
    # summaries
    # ------------------------------------------------------------------

    def score_line(self):
        return " | ".join(f"{p.name}: {p.lore} lore" for p in self.players)
