
from dataclasses import dataclass, field
from controller import Controller
from action import MulliganAction,InkAction,PlayCardAction,QuestAction,ChallengeAction,ChallengeTargetAction,TriggeredAbilityAction,AbilityTargetAction
from deck import Deck
from collections import Counter
from inplay_character import InPlayCharacter
from exceptions import TwentyLore
from decklists import CharacterCard,ItemCard
from inplay_card import InPlayItem
from inplay_ability import InPlayAbility
from ability import TriggeredAbility
from collections import Counter
import random

@dataclass
class Player:
    controller: Controller
    deck: Deck
    hand: list = field(default_factory=lambda: [])
    pending_mulligan: list = field(default_factory=lambda: [])
    ready_ink: int = 0
    exerted_ink: int = 0
    in_play_characters: list = field(default_factory=lambda: [])
    lore: int = 0
    discard: list = field(default_factory=lambda: [])
    in_play_items: list = field(default_factory=lambda: [])
    in_play_abilities: list = field(default_factory=lambda: [])

    def get_top_card_choices(self):
        return self.deck.get_card_choices()

    def draw_card(self,card):
        self.deck.draw_card(card)
        self.hand.append(card)
    
    def print_hand(self):
        for x in self.hand:
            print(x.name)

    def get_mulligans(self):
        card_counts = set(self.hand)
        return list(map(lambda x: MulliganAction(x), card_counts))

    def mulligan_card(self, card):
        self.hand.remove(card)
        self.pending_mulligan.append(card)

    def finish_mulligan(self):
        for x in self.pending_mulligan:
            self.deck.put_card_on_bottom(x)
        self.deck.shuffle()

    def get_ink_actions(self):
        inkable_cards = set(filter(lambda x: x.inkable, self.hand))
        return list(map(lambda y: InkAction(y), inkable_cards))

    def ink_card(self,card):
        self.hand.remove(card)
        self.ready_ink += 1

    def get_playable_cards(self):
        playable_cards = set(filter(lambda x: x.cost <= self.ready_ink, self.hand))
        return list(map(lambda y: PlayCardAction(y), playable_cards))
    
    def play_card_from_hand(self,card):
        if card.cost > self.ready_ink:
            raise ValueError("Insufficent ink")
        self.hand.remove(card)
        if type(card) is CharacterCard:
            new_char = InPlayCharacter(card)
            self.in_play_characters.append(new_char)
        elif type(card) is ItemCard:
            new_item = InPlayItem(card)
            self.in_play_items.append(new_item)
        self.ready_ink -= card.cost
        self.exerted_ink += card.cost
        for ab in card.abilities:
            if isinstance(ab, TriggeredAbility):
                self.in_play_abilities.append(TriggeredAbilityAction(ab,card))


    def ready_characters(self):
        for x in self.in_play_characters:
            x.ready = True

    def ready_ink_cards(self):
        self.ready_ink += self.exerted_ink
        self.exerted_ink = 0

    def get_questable_cards(self):
        ready_and_dry = filter(lambda x: x.ready and x.dry, self.in_play_characters)
        descriptors = map(lambda x: x.get_descriptor(), ready_and_dry)
        card_counts=Counter()
        quest_actions=[]
        for x in set(descriptors):
            print(x)
            card_counts[x[0]] += 1
            quest_actions.append(QuestAction(x[0], card_counts[x[0]]-1))
        return quest_actions

    def perform_quest(self,card):
        quest_char = next(filter(lambda x: x.card == card, self.in_play_characters))
        quest_char.ready = False
        self.lore += quest_char.card.lore
        if self.lore >= 20:
            raise TwentyLore()

    def has_exerted_characters(self):
        return any(filter(lambda x: not x.ready, self.in_play_characters))

    def get_challenger_choices(self):
        ready_and_dry = filter(lambda x: x.ready and x.dry, self.in_play_characters)
        return list(map(lambda y: ChallengeAction(y.card), ready_and_dry))

    def get_challenge_targets(self):
        exerted = filter(lambda x: not x.ready, self.in_play_characters)
        return list(map(lambda y: ChallengeTargetAction(y.card), exerted))
    

    def perform_challenge(self, challenger, challengee):
        challenger.ready = False
        challenger.damage += challengee.card.strength
        challengee.damage += challenger.card.strength

    def check_banish(self, character):
        if character.damage >= character.card.willpower:
            self.in_play_characters.remove(character)
            self.discard.append(character.card)
        
    def get_character(self, card):
        in_play_card = next(filter(lambda x: x.card == card, self.in_play_characters))
        return in_play_card

    def dry_characters(self):
        for x in self.in_play_characters:
            x.dry = True

    def get_triggerable_abilities(self):
        result=[]
        for ab in self.in_play_abilities:
            if type(ab.card) is ItemCard and\
                    ab.ability.needs_to_exert and \
                    any(x.ready and x.card == ab.card for x in self.in_play_items):
                result.append(ab)
        return result

    def get_targetable_characters(self):
        return self.in_play_characters





def create_player(contestant):
    return Player(contestant.controller, Deck(contestant.deck.cards))
