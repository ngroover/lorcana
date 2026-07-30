"""Main-phase actions.

Actions reference in-play cards by ``uid`` rather than by object identity so
that an action generated while searching on a cloned game can be replayed on the
real one.  They are frozen dataclasses, which makes them comparable and hashable
for exactly that purpose.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    def describe(self, game):  # pragma: no cover - overridden
        return str(self)


@dataclass(frozen=True)
class InkAction(Action):
    card: object

    def describe(self, game):
        return f"Ink {self.card.full_name} (cost {self.card.cost})"


@dataclass(frozen=True)
class PlayAction(Action):
    card: object

    def describe(self, game):
        cost = game.effective_cost(game.current_player, self.card)
        return f"Play {self.card.full_name} for {cost} ink"


@dataclass(frozen=True)
class ShiftAction(Action):
    card: object
    target_uid: int

    def describe(self, game):
        target = game.current_player.character_by_uid(self.target_uid)
        cost = self.card.keywords.get("Shift", self.card.cost)
        name = target.card.full_name if target else "?"
        return f"Shift {self.card.full_name} onto {name} for {cost} ink"


@dataclass(frozen=True)
class SingAction(Action):
    card: object       # the song
    singer_uid: int

    def describe(self, game):
        singer = game.current_player.character_by_uid(self.singer_uid)
        name = singer.card.full_name if singer else "?"
        return f"Sing {self.card.full_name} with {name} (free)"


@dataclass(frozen=True)
class QuestAction(Action):
    uid: int

    def describe(self, game):
        character = game.current_player.character_by_uid(self.uid)
        if character is None:
            return "Quest"
        return f"Quest with {character.card.full_name} (+{character.card.lore} lore)"


@dataclass(frozen=True)
class ChallengeAction(Action):
    uid: int
    target_uid: int

    def describe(self, game):
        attacker = game.current_player.character_by_uid(self.uid)
        defender = game.opponent_player.character_by_uid(self.target_uid)
        if attacker is None or defender is None:
            return "Challenge"
        power = game.strength_of(attacker, challenging=True)
        defence = game.strength_of(defender)
        left = defender.card.willpower - defender.damage
        mine = attacker.card.willpower - attacker.damage
        return (f"Challenge {defender.card.full_name} "
                f"with {attacker.card.full_name} "
                f"(deals {power} to {left} willpower; "
                f"takes {defence} of its own {mine})")


@dataclass(frozen=True)
class ActivateAction(Action):
    uid: int
    ability_index: int
    is_item: bool

    def describe(self, game):
        player = game.current_player
        source = player.item_by_uid(self.uid) if self.is_item else player.character_by_uid(self.uid)
        if source is None:
            return "Activate ability"
        ability = game.activated_abilities(source.card)[self.ability_index]
        return f"{source.card.full_name}: {ability.cost_description()} - {ability.text}"


@dataclass(frozen=True)
class PassAction(Action):
    def describe(self, game):
        return "Pass turn"
