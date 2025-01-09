class Utils:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def ajouter2(self, x):
        return x+self.y + 2

    def ajouter3(self, y):
        return self.x + y + 3

def ajouter(x, y):
    return x+y+0.5

x=0
y=0
# Je veux imprimer le chiffre 7.5 en n'utilisant QUE les variables, fonctions et objets définis ci-dessus.


print(y)
x = Utils(x, y).ajouter3(y)
x = Utils(x, y).ajouter2(x)
x = Utils(x, y).ajouter2(x)
y = ajouter(x, y)
