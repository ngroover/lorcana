
from dataclasses import dataclass
from decklists import Card

@dataclass
class SwapFirstPlayerAction:
    pass

@dataclass
class MulliganAction:
    card: Card
    
@dataclass
class PassAction:
    pass
