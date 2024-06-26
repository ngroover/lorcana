#!/usr/bin/python3
from dataclasses import dataclass
from decklists import Card
from inplay_card import InPlayCard

@dataclass
class InPlayCharacter(InPlayCard):
    dry: bool = False
    challenger_keyword: int = 0
    damage: int = 0
    evasive: bool = False
    cannot_quest_this_turn: bool = False
    
    # get a tuple descriptor so we can hash it
    def get_descriptor(self):
        return (self.card, self.ready, self.dry, self.damage)

    def has_evasive(self, game):
        if callable(self.evasive):
            return self.evasive(game, self)
        return self.evasive

