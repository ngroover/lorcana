#!/usr/bin/python3
from dataclasses import dataclass
from decklists import Card
from inplay_card import InPlayCard

@dataclass
class Ability:
    in_play_card : InPlayCard
