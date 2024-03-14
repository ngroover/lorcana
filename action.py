
from dataclasses import dataclass
from decklists import Card

# Action for environment to choose and swap who is first player or not
# this is usually 50/50 per die roll
@dataclass
class FirstPlayerAction:
    swap: bool
    weight: int = 1

@dataclass
class MulliganAction:
    card: Card
    
@dataclass
class PassAction:
    pass
