from dataclasses import dataclass
from decklists import Card

@dataclass
class InPlayCharacter:
    card: Card
    ready: bool = True
    dry: bool = False
    damage: int = 0

