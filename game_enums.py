#!/usr/bin/python3

from enum import Enum

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

