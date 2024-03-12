
from dataclasses import dataclass
from player import Player
from player import create_player
from enum import Enum
from action import MulliganAction,PassAction

import random

class GamePhase(Enum):
    MULLIGAN=1
    ACTION=2
    GAME_OVER=3

class PlayerTurn(Enum):
    PLAYER1=1
    PLAYER2=2

@dataclass
class Game:
    pl: Player
    p2: Player
    currentPlayer: Player
    phase: GamePhase
    player: PlayerTurn

    def __init__(self, contestant1, contestant2):
        self.p1 = create_player(contestant1)
        self.p2 = create_player(contestant2)
        if random.randint(1,2) == 1:
            self.p1, self.p2 = self.p2, self.p1
        self.currentPlayer = self.p1
        self.player = PlayerTurn.PLAYER1
        print(f'{self.currentPlayer.controller.name} goes first')
        self.p1.shuffle_deck()
        self.p2.shuffle_deck()
        self.p1.draw_cards(7)
        self.p2.draw_cards(7)
        self.phase = GamePhase.MULLIGAN

    def play_game(self):
        while self.phase != GamePhase.GAME_OVER:
            actions = self.get_actions()
            if len(actions) > 1:
                chosen_action = self.currentPlayer.controller.chooseAction(actions)
            else:
                chosen_action = actions[0]
            print(f'chosen action is {chosen_action}')
            self.process_action(chosen_action)

    def swap_current_player(self):
        if self.currentPlayer == self.p1:
            self.currentPlayer = self.p2
        else:
            self.currentPlayer = self.p1
        if self.player == PlayerTurn.PLAYER1:
            self.player = PlayerTurn.PLAYER2
        else:
            self.player = PlayerTurn.PLAYER1


    def process_action(self, act):
        if self.phase == GamePhase.MULLIGAN:
            self.process_mulligan(act)

    def process_mulligan(self,act):
        if type(act) is MulliganAction:
            self.currentPlayer.mulligan_card(act.card)
        elif type(act) is PassAction:
            self.currentPlayer.finish_mulligan()
            self.swap_current_player()
            if self.player == PlayerTurn.PLAYER1:
                self.phase = GamePhase.GAME_OVER


    def get_actions(self):
        if self.phase == GamePhase.MULLIGAN:
            mulligans=self.currentPlayer.get_mulligans()
            mulligans.append(PassAction())
            return mulligans

