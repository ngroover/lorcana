
from dataclasses import dataclass
from player import Player
from player import create_player
from enum import Enum
from action import MulliganAction,PassAction,FirstPlayerAction,DrawAction,InkAction,PlayCardAction,QuestAction,ChallengeAction
from controller import Controller
from exceptions import TwentyLore
from inplay_character import InPlayCharacter
from inplay_ability import InPlayAbility

import random

class GamePhase(Enum):
    DIE_ROLL=1
    DRAW_STARTING_HAND=2
    DRAW_PHASE=3
    MULLIGAN=4
    MAIN=5
    GAME_OVER=6
    CHALLENGING=7
    CHOOSE_TARGET=8

class PlayerTurn(Enum):
    PLAYER1=1
    PLAYER2=2

@dataclass
class Game:
    pl: Player
    p2: Player
    currentPlayer: Player
    currentOpponent: Player
    phase: GamePhase
    player: PlayerTurn
    environment: Controller
    currentController: Controller
    mulligan_finished: bool = False
    player_has_inked: bool = False
    current_challenger: InPlayCharacter = None
    winner: PlayerTurn = PlayerTurn.PLAYER1
    pending_ability: InPlayAbility = None

    def __init__(self, contestant1, contestant2, environment):
        self.environment = environment
        self.p1 = create_player(contestant1)
        self.p2 = create_player(contestant2)
        self.currentPlayer = self.p1
        self.currentOpponent = self.p2
        self.currentController = environment
        self.player = PlayerTurn.PLAYER1
        self.phase = GamePhase.DIE_ROLL

    def play_game(self):
        while self.phase != GamePhase.GAME_OVER:
            actions = self.get_actions()
            if len(actions) > 1:
                chosen_action = self.currentController.chooseAction(actions)
            else:
                chosen_action = actions[0]
            self.process_action(chosen_action)

    def swap_current_player(self):
        if self.currentPlayer == self.p1:
            if self.currentController.name != self.environment.name:
                self.currentController = self.p2.controller
            self.currentPlayer = self.p2
            self.currentOpponent = self.p1
        else:
            if self.currentController.name != self.environment.name:
                self.currentController = self.p1.controller
            self.currentPlayer = self.p1
            self.currentOpponent = self.p2
        if self.player == PlayerTurn.PLAYER1:
            self.player = PlayerTurn.PLAYER2
        else:
            self.player = PlayerTurn.PLAYER1


    def process_action(self, act):
        try:
            if self.phase == GamePhase.MULLIGAN:
                self.process_mulligan(act)
            elif self.phase == GamePhase.DRAW_STARTING_HAND:
                self.currentPlayer.controller.logMessage(f"You draw {act.card}")
                your_name = self.currentPlayer.controller.name
                self.currentOpponent.controller.logMessage(f"{your_name} draws a card")
                self.currentPlayer.draw_card(act.card)
                if len(self.p1.hand) == 7 and len(self.p2.hand) == 7:
                    #technically i think the pending mulligan cards go
                    # on the bottom of the deck before you draw but it doesn't matter
                    self.p1.finish_mulligan()
                    self.p2.finish_mulligan()
                    if self.player == PlayerTurn.PLAYER2:
                        self.swap_current_player()
                    if self.mulligan_finished:
                        self.currentController = self.p1.controller
                        self.phase = GamePhase.MAIN
                    else:
                        self.currentController = self.p1.controller
                        self.player = PlayerTurn.PLAYER1
                        self.currentPlayer = self.p1
                        self.phase = GamePhase.MULLIGAN
                else:
                    if len(self.currentPlayer.hand) == 7:
                        self.swap_current_player()
            elif self.phase == GamePhase.DIE_ROLL:
                self.do_die_roll(act)
            elif self.phase == GamePhase.MAIN:
                self.do_main_action(act)
            elif self.phase == GamePhase.DRAW_PHASE:
                self.currentPlayer.draw_card(act.card)
                self.currentController = self.currentPlayer.controller
                self.phase = GamePhase.MAIN
                self.currentPlayer.ready_characters()
                self.currentPlayer.ready_ink_cards()
                self.currentPlayer.dry_characters()
                self.player_has_inked = False
            elif self.phase == GamePhase.CHALLENGING:
                challengee = self.currentOpponent.get_character(act.card)
                self.currentPlayer.perform_challenge(self.current_challenger,
                        challengee)
                self.currentPlayer.check_banish(self.current_challenger)
                self.currentOpponent.check_banish(challengee)
                self.current_challenger = None
                self.phase = GamePhase.MAIN
        except TwentyLore as tl:
            self.phase = GamePhase.GAME_OVER
            if self.p1.lore >= 20:
                self.winner = PlayerTurn.PLAYER1
            else:
                self.winner = PlayerTurn.PLAYER2
            


    def do_main_action(self,act):
        if type(act) is InkAction:
            your_name = self.currentPlayer.controller.name
            self.log_both_players(f"{your_name} inked {act.card}")
            self.player_has_inked = True
            self.currentPlayer.ink_card(act.card)
        elif type(act) is PlayCardAction:
            your_name = self.currentPlayer.controller.name
            self.log_both_players(f'{your_name} played {act.card} from hand')
            self.currentPlayer.play_card_from_hand(act.card)
                
        elif type(act) is PassAction:
            # Do end of turn stuff and start over turn stuff
            # for other player
            your_name = self.currentPlayer.controller.name
            self.log_both_players(f'{your_name} passed turn')
            self.swap_current_player()
            self.currentController = self.environment
            if self.currentPlayer.deck.get_total_cards() == 0:
                self.phase = GamePhase.GAME_OVER
                if self.player == PlayerTurn.PLAYER1:
                    self.winner = PlayerTurn.PLAYER2
                else:
                    self.winner = PlayerTurn.PLAYER1
            else:
                self.phase = GamePhase.DRAW_PHASE
        elif type(act) is QuestAction:
            your_name = self.currentPlayer.controller.name
            self.currentPlayer.perform_quest(act.card)
            your_lore = self.currentPlayer.lore
            self.log_both_players(f'{your_name} quested with {act.card} (lore: {your_lore})')
        elif type(act) is ChallengeAction:
            self.current_challenger = self.currentPlayer.get_character(act.card)
            self.phase = GamePhase.CHALLENGING

    def log_both_players(self, log):
        self.p1.controller.logMessage(log)
        self.p2.controller.logMessage(log)

    def do_die_roll(self,act):
        if type(act) is FirstPlayerAction and act.swap:
            # swap who goes first
            self.p1, self.p2 = self.p2, self.p1
        self.currentPlayer = self.p1
        self.currentOpponent = self.p2
        self.player = PlayerTurn.PLAYER1
        self.phase = GamePhase.DRAW_STARTING_HAND
        self.log_both_players(f'{self.currentPlayer.controller.name} goes first')

    def process_mulligan(self,act):
        if type(act) is MulliganAction:
            self.currentPlayer.controller.logMessage(f"You mulliganed {act.card}")
            your_name = self.currentPlayer.controller.name
            self.currentOpponent.controller.logMessage(f"{your_name} mulliganed a card")
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
                    self.currentController = self.environment
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
        elif self.phase == GamePhase.DRAW_STARTING_HAND or self.phase == GamePhase.DRAW_PHASE:
            card_choices = self.currentPlayer.get_top_card_choices()
            return list(map(lambda card_choice: DrawAction(card_choice[0],card_choice[1]), card_choices.items()))
        elif self.phase == GamePhase.MAIN:
            ink_actions=[]
            challenger_actions=[]
            triggered_abilities=[]
            if not self.player_has_inked:
                ink_actions=self.currentPlayer.get_ink_actions()
            playable_cards=self.currentPlayer.get_playable_cards()
            questable_cards=self.currentPlayer.get_questable_cards()
            if self.currentOpponent.has_exerted_characters():
                challenger_actions=self.currentPlayer.get_challenger_choices()
            triggered_abilities=self.currentPlayer.get_triggerable_abilities()
            return ink_actions + playable_cards + questable_cards + challenger_actions + triggered_abilities + [PassAction()]
        elif self.phase == GamePhase.CHALLENGING:
            return self.currentOpponent.get_challenge_targets()





