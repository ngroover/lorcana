
from dataclasses import dataclass
from player import Player
from player import create_player
from enum import Enum
from action import MulliganAction,PassAction,SwapFirstPlayerAction
from controller import Controller

import random

class GamePhase(Enum):
    DIE_ROLL=1
    DRAW_STARTING_HAND=2
    MULLIGAN=3
    ACTION=4
    GAME_OVER=5

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
    environment: Controller

    def __init__(self, contestant1, contestant2, environment):
        self.environment = environment
        self.p1 = create_player(contestant1)
        self.p2 = create_player(contestant2)
        self.currentPlayer = self.p1
        self.player = PlayerTurn.PLAYER1
        self.phase = GamePhase.DIE_ROLL
        #print(f'{self.currentPlayer.controller.name} goes first')
        #self.p1.shuffle_deck()
        #self.p2.shuffle_deck()
        #self.p1.draw_cards(7)
        #self.p2.draw_cards(7)

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
        elif self.phase == GamePhase.DIE_ROLL:
            self.do_die_roll(act)

    def do_die_roll(self,act):
        if type(act) is SwapFirstPlayerAction:
            # swap who goes first
            self.p1, self.p2 = self.p2, self.p1
        self.phase = GamePhase.DRAW_STARTING_HAND

    def process_mulligan(self,act):
        if type(act) is MulliganAction:
            self.currentPlayer.mulligan_card(act.card)
        elif type(act) is PassAction:
            self.currentPlayer.finish_mulligan()
            self.swap_current_player()
            if self.player == PlayerTurn.PLAYER1:
                self.phase = GamePhase.GAME_OVER

    def get_controller(self):
        if self.phase == GamePhase.DIE_ROLL:
            return self.environment
        elif self.player == PlayerTurn.PLAYER1:
            return self.p1.controller
        else:
            return self.p2.controller

    def get_actions(self):
        if self.phase == GamePhase.MULLIGAN:
            mulligans=self.currentPlayer.get_mulligans()
            mulligans.append(PassAction())
            return mulligans
        elif self.phase == GamePhase.DIE_ROLL:
            return [SwapFirstPlayerAction(), PassAction()]

