
from contestant import Contestant
from decklists import amber_amethyst,sapphire_steel
from controller import RandomController,Controller
from game import Game

def test_contestants():
    c1 = Contestant(amber_amethyst, RandomController('test1'))
    c2 = Contestant(sapphire_steel, RandomController('test2'))
    return [c1,c2]

def simple_test_game():
    c = test_contestants()
    game = Game(c[0],c[1],RandomController('env'))
    return game

