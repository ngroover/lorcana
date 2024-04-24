#!/usr/bin/python3
from dataclasses import dataclass

@dataclass(frozen=True)
class Ability:
    needs_target : bool = True


@dataclass(frozen=True)
class PassiveAbility(Ability):
    pass

@dataclass(frozen=True)
class GainEvasiveAbility(PassiveAbility):
    def has_evasive(self, game, inplay_character):
        return True

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

