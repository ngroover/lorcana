#!/usr/bin/python3
from dataclasses import dataclass

@dataclass(frozen=True)
class Ability:
    needs_target : bool = True


@dataclass(frozen=True)
class OnPlayAbility(Ability):
    pass

@dataclass(frozen=True)
class TriggeredAbility(Ability):
    needs_to_exert : bool = True

@dataclass(frozen=True)
class HealingTriggeredAbility(TriggeredAbility):
    healing_power : int = 1

