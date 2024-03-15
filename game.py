
from dataclasses import dataclass
from player import Player
from player import create_player
from enum import Enum
from action import MulliganAction,PassAction,FirstPlayerAction,DrawAction,InkAction,PlayCardAction
from controller import Controller

import random

class GamePhase(Enum):
    DIE_ROLL=1
    DRAW_STARTING_HAND=2
    MULLIGAN=3
    MAIN=4
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
    currentController: Controller
    mulligan_finished: bool = False

    def __init__(self, contestant1, contestant2, environment):
        self.environment = environment
        self.p1 = create_player(contestant1)
        self.p2 = create_player(contestant2)
        self.currentPlayer = self.p1
        self.currentController = environment
        self.player = PlayerTurn.PLAYER1
        self.phase = GamePhase.DIE_ROLL

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
        elif self.phase == GamePhase.DRAW_STARTING_HAND:
            self.currentPlayer.draw_card(act.card)
            if len(self.p1.hand) == 7 and len(self.p2.hand) == 7:
                #technically i think the pending mulligan cards go
                # on the bottom of the deck before you draw but it doesn't matter
                self.p1.finish_mulligan()
                self.p2.finish_mulligan()
                if self.player == PlayerTurn.PLAYER2:
                    self.swap_current_player()
                if self.mulligan_finished:
                    self.phase = GamePhase.MAIN
                else:
                    self.phase = GamePhase.MULLIGAN
            else:
                if len(self.currentPlayer.hand) == 7:
                    self.swap_current_player()
        elif self.phase == GamePhase.DIE_ROLL:
            self.do_die_roll(act)
        elif self.phase == GamePhase.MAIN:
            self.do_main_action(act)
    def do_main_action(self,act):
        if type(act) is InkAction:
            self.currentPlayer.ink_card(act.card)
        elif type(act) is PlayCardAction:
            self.currentPlayer.play_card_from_hand(act.card)

    def do_die_roll(self,act):
        if type(act) is FirstPlayerAction and act.swap:
            # swap who goes first
            self.p1, self.p2 = self.p2, self.p1
        self.phase = GamePhase.DRAW_STARTING_HAND

    def process_mulligan(self,act):
        if type(act) is MulliganAction:
            self.currentPlayer.mulligan_card(act.card)
        elif type(act) is PassAction:
            self.mulligan_finished=True
            self.swap_current_player()
            # going into draw phase now or maybe skipping to main phase
            if self.player == PlayerTurn.PLAYER1:
                if len(self.currentPlayer.hand) == 7:
                    self.swap_current_player()
                if len(self.currentPlayer.hand) == 7:
                    self.swap_current_player()
                    self.phase = GamePhase.MAIN
                else:
                    self.phase = GamePhase.DRAW_STARTING_HAND


    def get_controller(self):
        return self.currentController

    def get_actions(self):
        if self.phase == GamePhase.MULLIGAN:
            mulligans=self.currentPlayer.get_mulligans()
            mulligans.append(PassAction())
            return mulligans
        elif self.phase == GamePhase.DIE_ROLL:
            return [FirstPlayerAction(True), FirstPlayerAction(False)]
        elif self.phase == GamePhase.DRAW_STARTING_HAND:
            card_choices = self.currentPlayer.get_top_card_choices()
            return list(map(lambda card_choice: DrawAction(card_choice[0],card_choice[1]), card_choices.items()))
        elif self.phase == GamePhase.MAIN:
            ink_actions=self.currentPlayer.get_ink_actions()
            playable_cards=self.currentPlayer.get_playable_cards()
            return ink_actions + playable_cards



