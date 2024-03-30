#!/usr/bin/python3
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from decklists import olaf,pascal,captain_hook,aurora,maleficent,fire_the_cannons,dinglehopper
from action import FirstPlayerAction,DrawAction,PassAction,InkAction,PlayCardAction,QuestAction,TriggeredAbilityAction,AbilityTargetAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility

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

    def ink_hook(self):
        self.game.process_action(InkAction(captain_hook))
        return self

    def quest_hook(self):
        self.game.process_action(QuestAction(captain_hook))
        return self

    def play_hook(self):
        self.game.process_action(PlayCardAction(captain_hook))
        return self

    def use_dinglehopper(self):
        self.game.process_action(TriggeredAbilityAction(HealingTriggeredAbility(),dinglehopper))
        return self

    def olaf_challenge_hook(self):
        self.game.process_action(ChallengeAction(olaf))
        self.game.process_action(ChallengeTargetAction(captain_hook))
        return self

    def play_olaf(self):
        self.game.process_action(PlayCardAction(olaf))
        return self

    def ink_olaf(self):
        self.game.process_action(InkAction(olaf))
        return self

    def quest_hook(self):
        self.game.process_action(QuestAction(captain_hook))
        return self

    def play_dinglehopper(self):
        self.game.process_action(PlayCardAction(dinglehopper))
        return self

    def target_olaf(self):
        self.game.process_action(AbilityTargetAction(olaf))
        return self


    def pass_turn(self):
        self.game.process_action(PassAction())
        cards_to_draw = self.game.get_actions()
        # draw whatever card. doesn't matter
        self.game.process_action(cards_to_draw[0])
        return self



