import random

class Controller:
    def __init__(self, name, print_logs):
        self.name = name
        self.print_logs = print_logs

    def logMessage(self,msg):
        if self.print_logs:
            print(f'{self.name}: {msg}')

class HumanController(Controller):
    def __init__(self, name, print_logs=False):
        super().__init__(name,print_logs)

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
    def __init__(self, name, print_logs=False):
        super().__init__(name,print_logs)

    def chooseAction(self, actions):
        act = random.choice(actions)
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
        return HumanController(name, print_logs=True)
    else:
        return RandomController(name, print_logs=True)

    
    
