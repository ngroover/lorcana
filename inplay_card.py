#!/usr/bin/python3
from dataclasses import dataclass
from decklists import Card

@dataclass
class InPlayCard:
    card: Card
    ready: bool = True

@dataclass
class InPlayItem(InPlayCard):
    pass
