
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController,Controller
from game import Game,GamePhase,PlayerTurn
from decklists import olaf,pascal,hades,part_of_your_world,rafiki
from decklists import captain_hook,flounder,one_jump_ahead,fire_the_cannons,mickey_mouse_true_friend,kristoff
from inplay_character import InPlayCharacter


def test_contestants():
    c1 = Contestant(amber_amethyst, RandomController('test1'))
    c2 = Contestant(sapphire_steel, RandomController('test2'))
    return [c1,c2]

def simple_test_game():
    c = test_contestants()
    game = Game(c[0],c[1],RandomController('env'))
    return game

def draw_opening_hand_game(first_player_swap, p1_hand, p2_hand):
    game = simple_test_game()

    game.process_action(FirstPlayerAction(first_player_swap))

    if first_player_swap:
        all_cards=p2_hand+p1_hand
    else:
        all_cards=p1_hand+p2_hand
    for x in all_cards:
        game.process_action(DrawAction(x))

    return game

def main_state_with_half_inkables_game():
    g = simple_test_game()
    g.phase = GamePhase.MAIN
    g.player = PlayerTurn.PLAYER1
    g.currentPlayer = g.p1
    g.currentOpponent = g.p2

    g.p1.hand = [olaf,olaf,olaf,pascal,hades,part_of_your_world,rafiki]
    g.p2.hand = [captain_hook,captain_hook,captain_hook,flounder,one_jump_ahead,one_jump_ahead,fire_the_cannons]

    # draw cards from deck so the game is consistent
    for x in g.p1.hand:
        g.p1.deck.draw_card(x)
    for y in g.p2.hand:
        g.p2.deck.draw_card(y)

    return g

def main_state_with_some_characters_in_play():
    g = simple_test_game()
    g.phase = GamePhase.MAIN
    g.player = PlayerTurn.PLAYER1
    g.currentPlayer = g.p1
    g.currentOpponent = g.p2

    g.p1.hand = [olaf,olaf,olaf,pascal,hades,part_of_your_world,rafiki]
    g.p2.hand = [captain_hook,captain_hook,captain_hook,flounder,one_jump_ahead,one_jump_ahead,fire_the_cannons]

    # draw cards from deck so the game is consistent
    for x in g.p1.hand:
        g.p1.deck.draw_card(x)
    for y in g.p2.hand:
        g.p2.deck.draw_card(y)

    g.p1.hand.remove(olaf)
    g.p1.hand.remove(pascal)
    g.p1.hand.remove(hades)
    g.p2.hand.remove(captain_hook)
    g.p2.hand.remove(flounder)
    g.p1.in_play_characters.append(InPlayCharacter(olaf, dry=True))
    g.p1.in_play_characters.append(InPlayCharacter(pascal, dry=True))
    g.p1.in_play_characters.append(InPlayCharacter(hades, dry=False))
    g.p2.in_play_characters.append(InPlayCharacter(captain_hook, dry=True))
    g.p2.in_play_characters.append(InPlayCharacter(flounder, dry=True, ready=False))

    return g

def main_state_with_some_characters_in_play_p2():
    g = simple_test_game()
    g.phase = GamePhase.MAIN
    g.player = PlayerTurn.PLAYER2
    g.currentPlayer = g.p2
    g.currentOpponent = g.p1

    g.p1.hand = [pascal]
    g.p2.hand = [flounder]

    # draw cards from deck so the game is consistent
    for x in g.p1.hand:
        g.p1.deck.draw_card(x)
    for y in g.p2.hand:
        g.p2.deck.draw_card(y)

    g.p1.hand.remove(pascal)
    g.p2.hand.remove(flounder)
    g.p1.in_play_characters.append(InPlayCharacter(pascal, dry=True, ready=False))
    g.p2.in_play_characters.append(InPlayCharacter(flounder, dry=True, ready=True))

    return g

def main_state_with_some_characters_in_play_p1():
    g = simple_test_game()
    g.phase = GamePhase.MAIN
    g.player = PlayerTurn.PLAYER1
    g.currentPlayer = g.p1
    g.currentOpponent = g.p2

    g.p1.hand = [mickey_mouse_true_friend]
    g.p2.hand = [kristoff]

    # draw cards from deck so the game is consistent
    for x in g.p1.hand:
        g.p1.deck.draw_card(x)
    for y in g.p2.hand:
        g.p2.deck.draw_card(y)

    g.p1.hand.remove(mickey_mouse_true_friend)
    g.p2.hand.remove(kristoff)
    g.p1.in_play_characters.append(InPlayCharacter(mickey_mouse_true_friend, dry=True, ready=True))
    g.p2.in_play_characters.append(InPlayCharacter(kristoff, dry=True, ready=False))

    return g

def main_state_with_p2_no_cards():
    g = simple_test_game()
    g.phase = GamePhase.MAIN
    g.player = PlayerTurn.PLAYER1
    g.currentPlayer = g.p1
    g.currentOpponent = g.p2

    g.p1.hand = [olaf,olaf,olaf,pascal,hades,part_of_your_world,rafiki]
    g.p2.hand = [captain_hook,captain_hook,captain_hook,flounder,one_jump_ahead,one_jump_ahead,fire_the_cannons]

    # draw cards from deck so the game is consistent
    for x in g.p1.hand:
        g.p1.deck.draw_card(x)
    for y in g.p2.hand:
        g.p2.deck.draw_card(y)
    g.p2.deck.clear()

    return g

