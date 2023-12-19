from SystemData import SystemData
from z3 import *
from ManualCNFConversion import *

o = Optimize()
x = Int('x')
o.add(And(x > 0, x < 5))
y = Bool('Low')
o.add(Implies(y, (x < 4)))
o.assert_exprs(y)

o.maximize(x)
print(o.check())  # prints sat
print(o.model())  # prints [x = 4]

class SMTSolver:
    def __init__(self, systemData):
        models = "../data/RIS-FOP/"
        self.s = SystemData(featuresFile=models + 'features.txt')
        self.solver = Optimize()
        self.clauses = []
        features = []
        for feature in self.s.getFeatures():
            features.append(Bool(feature))

        for constraint in self.s.getConstraints():
            helper = switcher.get(constraint[0].lower(), lambda: print("Invalid constraint."))
            newClauses = helper(self.s.toIndex(constraint[1]), self.s.toIndex(constraint[2]))
            self.clauses = self.clauses + newClauses
        # Adding clauses already in CNF form.
        self.clauses = self.clauses + self.s.getCNFConstraints()

        for clause in self.clauses:
            self.solver.check(clause)

SMTSolver("truc")

