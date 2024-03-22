#!/usr/bin/python3
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from decklists import olaf,pascal,captain_hook,aurora,maleficent,fire_the_cannons,dinglehopper
from action import FirstPlayerAction,DrawAction,PassAction,InkAction,PlayCardAction,QuestAction

class DinglehopperGameGenerator:
    def test_contestants(self):
        c1 = Contestant(amber_amethyst, RandomController('test1'))
        c2 = Contestant(sapphire_steel, RandomController('test2'))
        return [c1,c2]

    def init_game(self):
        c = self.test_contestants()
        self.game = Game(c[0],c[1],RandomController('env'))
        return self

    def draw_opening_hand(self):
        first_player_swap=False
        p1_hand=[olaf,olaf,olaf,pascal,pascal,dinglehopper,dinglehopper]
        p2_hand=[captain_hook,captain_hook,captain_hook, aurora, maleficent, maleficent,maleficent]

        self.game.process_action(FirstPlayerAction(first_player_swap))

        if first_player_swap:
            all_cards=p2_hand+p1_hand
        else:
            all_cards=p1_hand+p2_hand
        for x in all_cards:
            self.game.process_action(DrawAction(x))

        return self

    def pass_mulligan(self):
        self.game.process_action(PassAction())
        self.game.process_action(PassAction())
        return self

    def play_olaf(self):
        self.game.process_action(PlayCardAction(olaf))
        return self

    def ink_olaf(self):
        self.game.process_action(InkAction(olaf))
        return self


    def play_olaf_pass(self):
        self.game.process_action(InkAction(olaf))
        self.game.process_action(PlayCardAction(olaf))
        self.game.process_action(PassAction())
        self.game.process_action(DrawAction(fire_the_cannons))
        return self

    def quest_olaf_pass(self):
        self.game.process_action(QuestAction(olaf))
        self.game.process_action(PassAction())
        self.game.process_action(DrawAction(fire_the_cannons))
        return self

    def p1_pass(self):
        self.game.process_action(PassAction())
        self.game.process_action(DrawAction(fire_the_cannons))
        return self

    def p2_pass(self):
        self.game.process_action(PassAction())
        self.game.process_action(DrawAction(dinglehopper))
        return self


