#!/usr/bin/python3
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from decklists import olaf,pascal,captain_hook,aurora,maleficent,fire_the_cannons,dinglehopper,flounder
from action import FirstPlayerAction,DrawAction,PassAction,InkAction,PlayCardAction,QuestAction,TriggeredAbilityAction,AbilityTargetAction,ChallengeAction,ChallengeTargetAction
from ability import HealingTriggeredAbility

class GameGenerator:
    def test_contestants(self, deck1, deck2):
        c1 = Contestant(deck1, RandomController('test1'))
        c2 = Contestant(deck2, RandomController('test2'))
        return [c1,c2]

    def init_game(self, deck1, deck2):
        c = self.test_contestants(deck1, deck2)
        self.game = Game(c[0],c[1],RandomController('env'))
        return self

    def draw_inkable(self):
        actions = self.game.get_actions()

        for a in actions:
            if isinstance(a, DrawAction) and a.card.inkable:
                self.game.process_action(a)
                break


    def setup_cards(self, p1_cards, p2_cards, minimum_ink=0):
        if self.game.phase != GamePhase.DIE_ROLL:
            raise ValueError("setup_cards must be called from DIE_ROLL State")
        
        p1_cards_to_draw = p1_cards.copy()
        p2_cards_to_draw = p2_cards.copy()

        self.game.process_action(FirstPlayerAction(False))

        # p1 cards to draw
        for x in range(7):
            if len(p1_cards_to_draw) > 0:
                self.game.process_action(DrawAction(p1_cards_to_draw.pop()))
            else:
                self.draw_inkable()

        # p2 cards to draw
        for x in range(7):
            if len(p2_cards_to_draw) > 0:
                self.game.process_action(DrawAction(p2_cards_to_draw.pop()))
            else:
                self.draw_inkable()

        # pass mulligan
        self.game.process_action(PassAction())
        self.game.process_action(PassAction())

        p1_cards_to_play = p1_cards.copy()
        p2_cards_to_play = p2_cards.copy()

        while len(p1_cards_to_play) > 0 or len(p2_cards_to_play) > 0 and minimum_ink > self.game.p1.ready_ink or minimum_ink > self.game.p2.ready_ink:
            #p1 ink
            for a in self.game.get_actions():
                if isinstance(a, InkAction) and a.card not in p1_cards_to_play:
                    self.game.process_action(a)
                    break
            #p1 play
            for a in self.game.get_actions():
                if isinstance(a, PlayCardAction) and a.card in p1_cards_to_play:
                    self.game.process_action(a)
                    p1_cards_to_play.remove(a.card)
                    break
            self.game.process_action(PassAction())
            self.draw_inkable()
            #p2 ink
            for a in self.game.get_actions():
                if isinstance(a, InkAction) and a.card not in p2_cards_to_play:
                    self.game.process_action(a)
                    break
            #p2 play
            for a in self.game.get_actions():
                if isinstance(a, PlayCardAction) and a.card in p2_cards_to_play:
                    self.game.process_action(a)
                    p2_cards_to_play.remove(a.card)
            self.game.process_action(PassAction())
            self.draw_inkable()

        # dry the characters
        self.game.process_action(PassAction())
        self.draw_inkable()
        self.game.process_action(PassAction())
        self.draw_inkable()

        return self

    def pass_mulligan(self):
        self.game.process_action(PassAction())
        self.game.process_action(PassAction())
        return self

    def challenge(self, card):
        self.game.process_action(ChallengeAction(card))
        return self

    def ink_pascal(self):
        self.game.process_action(InkAction(pascal))
        return self

    def ink_hook(self):
        self.game.process_action(InkAction(captain_hook))
        return self

    def play_card(self, card):
        self.game.process_action(PlayCardAction(card))
        return self

    def play_hook(self):
        self.game.process_action(PlayCardAction(captain_hook))
        return self

    def play_flounder(self):
        self.game.process_action(PlayCardAction(flounder))
        return self
        

    def use_dinglehopper(self):
        self.game.process_action(TriggeredAbilityAction(HealingTriggeredAbility(),dinglehopper))
        return self

    def olaf_challenge_hook(self):
        self.game.process_action(ChallengeAction(olaf))
        self.game.process_action(ChallengeTargetAction(captain_hook))
        return self

    def olaf_challenge_hook(self, index):
        self.game.process_action(ChallengeAction(olaf, index))
        self.game.process_action(ChallengeTargetAction(captain_hook))
        return self

    def olaf_challenge_flounder(self,index):
        self.game.process_action(ChallengeAction(olaf,index))
        self.game.process_action(ChallengeTargetAction(flounder))
        return self

    def hook_challenge_olaf(self):
        self.game.process_action(ChallengeAction(captain_hook))
        self.game.process_action(ChallengeTargetAction(olaf))
        return self

    def flounder_challenge_olaf(self):
        self.game.process_action(ChallengeAction(flounder))
        self.game.process_action(ChallengeTargetAction(olaf))
        return self

    def challenge_target(self, card):
        self.game.process_action(ChallengeTargetAction(card))
        return self

    def target(self, card, player, index=0):
        self.game.process_action(AbilityTargetAction(card, player, index))
        return self

    def quest(self, card, index=0):
        self.game.process_action(QuestAction(card,index))
        return self

    def challenge(self, card, index=0):
        self.game.process_action(ChallengeAction(card,index))
        return self

    def draw_card(self,card):
        self.game.process_action(DrawAction(card))
        return self

    def pass_turn(self):
        self.game.process_action(PassAction())
        return self

    def pass_turn_draw(self):
        self.game.process_action(PassAction())
        cards_to_draw = self.game.get_actions()
        # draw whatever card. doesn't matter
        self.game.process_action(cards_to_draw[0])
        return self




