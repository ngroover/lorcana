#!/usr/bin/python3
from dataclasses import dataclass

@dataclass(frozen=True)
class Ability:
    needs_target : bool = True


@dataclass(frozen=True)
class PassiveAbility(Ability):
    pass

@dataclass(frozen=True)
class GainEvasiveAbility(Ability):
    pass

@dataclass(frozen=True)
class PascalGainEvasiveAbility(GainEvasiveAbility):
    def has_evasive(self, game, inplay_character):
        if inplay_character in game.p1.in_play_characters:
            return len(game.p1.in_play_characters) >= 2
        if inplay_character in game.p2.in_play_characters:
            return len(game.p2.in_play_characters) >= 2
        return False

@dataclass(frozen=True)
class OnPlayAbility(Ability):
    pass

@dataclass(frozen=True)
class TriggeredAbility(Ability):
    needs_to_exert : bool = True

@dataclass(frozen=True)
class HealingTriggeredAbility(TriggeredAbility):
    healing_power : int = 1

    def perform_ability(self, in_play_character):
        in_play_character.damage -= 1
        if in_play_character.damage < 0:
            in_play_character.damage = 0

@dataclass(frozen=True)
class OnQuestAbility(Ability):
    pass

@dataclass(frozen=True)
class ReadyPrincessAbility(OnQuestAbility):
    def on_quest(self, game, in_play_character):
        for char in game.currentPlayer.in_play_characters:
            if "Princess" in char.card.traits and char != in_play_character:
                char.cannot_quest_this_turn = True
                char.ready = True

