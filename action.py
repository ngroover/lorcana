
from dataclasses import dataclass
from decklists import Card

@dataclass
class MulliganAction:
    card: Card
    
@dataclass
class PassAction:
    pass
