import random

class Controller:
    def __init__(self, name):
        self.name = name

class HumanController(Controller):
    def __init__(self, name):
        super().__init__(name)

    def chooseAction(self, actions):
        for i,a in enumerate(actions):
            print(f'[{i+1}]. {a}')
        while True:
            try:
                choice = int(input("Choice: "))-1
                if choice >= 0 and choice < len(actions):
                    break
            except ValueError:
                #try again
                pass
        return actions[choice]

class RandomController(Controller):
    def __init__(self, name):
        super().__init__(name)

    def chooseAction(self, actions):
        act = random.choice(actions)
        print(f'{self.name} chose {act}')
        return act


def create_controller():
    name = input("Name:")
    print('Controller')
    print('[1]. Human')
    print('[2]. Random')
    while True:
        choice = int(input("Choice: "))
        if choice >=0 and choice <= 2:
            break
    if choice == 1:
        return HumanController(name)
    else:
        return RandomController(name)

    
    
