
class Controller:
    def __init__(self, name):
        self.name = name

class HumanController(Controller):
    def __init__(self, name):
        super().__init__(name)

    def chooseAction():
        pass

class RandomController(Controller):
    def __init__(self, name):
        super().__init__(name)

    def chooseAction():
        pass

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

    
    
