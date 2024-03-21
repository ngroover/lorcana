#!/usr/bin/python3
from dataclasses import dataclass
from decklists import Card
from inplay_card import InPlayCard

@dataclass
class InPlayCharacter(InPlayCard):
    dry: bool = False
    damage: int = 0

