#!/usr/bin/python3
from dataclasses import dataclass

@dataclass(frozen=True)
class Ability:
    needs_target : bool = True

    def can_use(self):
        return not in_play_card.exerted

@dataclass(frozen=True)
class OnPlayAbility(Ability):
    pass

@dataclass(frozen=True)
class TriggeredAbility(Ability):
    pass

@dataclass(frozen=True)
class HealingTriggeredAbility(TriggeredAbility):
    healing_power : int = 1

