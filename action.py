
from dataclasses import dataclass
from decklists import Card
from ability import TriggeredAbility
from game_enums import PlayerTurn

# Action for environment to choose and swap who is first player or not
# this is usually 50/50 per die roll
@dataclass(frozen=True)
class FirstPlayerAction:
    swap: bool
    weight: int = 1

@dataclass(frozen=True)
class DrawAction:
    card: Card
    weight: int = 1
    def __str__(self):
        return f"Draw {self.card}"

@dataclass(frozen=True)
class MulliganAction:
    card: Card

    def __str__(self):
        return f"Mulligan {self.card}"

@dataclass(frozen=True)
class InkAction:
    card: Card
    
@dataclass(frozen=True)
class PassAction:
    def __str__(self):
        return "Pass"

@dataclass(frozen=True)
class PlayCardAction:
    card: Card

@dataclass(frozen=True)
class QuestAction:
    card: Card
    index: int = 0

@dataclass(frozen=True)
class ChallengeAction:
    card: Card

@dataclass(frozen=True)
class ChallengeTargetAction:
    card: Card

@dataclass(frozen=True)
class TriggeredAbilityAction:
    ability: TriggeredAbility
    card: Card

@dataclass(frozen=True)
class AbilityTargetAction:
    target_card: Card
    player: PlayerTurn


