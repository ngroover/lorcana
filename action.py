
from dataclasses import dataclass
from decklists import Card

# Action for environment to choose and swap who is first player or not
# this is usually 50/50 per die roll
@dataclass(frozen=True)
class FirstPlayerAction:
    swap: bool
    weight: int = 1

@dataclass(frozen=True)
class DrawAction:
    card: Card
    weight: int

@dataclass(frozen=True)
class MulliganAction:
    card: Card

@dataclass(frozen=True)
class InkAction:
    card: Card
    
@dataclass(frozen=True)
class PassAction:
    pass

@dataclass(frozen=True)
class PlayAction:
    card: Card

