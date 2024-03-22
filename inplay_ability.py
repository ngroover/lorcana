#!/usr/bin/python3
from dataclasses import dataclass
from decklists import Card
from ability import Ability

@dataclass
class InPlayAbility:
    in_play_card: Card
    ability: Ability


