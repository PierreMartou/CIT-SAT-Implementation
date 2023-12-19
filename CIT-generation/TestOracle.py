from SystemData import SystemData
from z3 import *
from ManualCNFConversion import *


def firstTry():
    o = Optimize()
    x = Int('xez-0')
    o.add(And(x > 0, x < 5))
    y = Bool('Low')
    o.add(Implies(y, (x < 4)))
    o.assert_exprs(y)

    o.maximize(x)
    print(o.check())  # prints sat
    print(o.model())  # prints [x = 4]


class OracleSolver:
    def __init__(self, systemData, states):

        self.s = systemData
        self.solver = Optimize()
        self.clauses = []
        self.featuresInStates = []

        self.startFeatures = self.addState("start")
        self.finalFeatures = self.addState("final")
        for i in range(states):
            self.featuresInStates.append(self.addState(i))

        self.objective = self.createObjectives()
        self.solver.push()

    def addState(self, state):
        features = []
        for feature in self.s.getNodes():
            if str(state) in feature:
                print("warning, id in feature when creating SMT solver")
            if "-" in feature:
                print("warning, symbol - is not allowed in features")
            features.append(Bool(feature+"-"+str(state)))

        for constraint in self.s.getConstraints():
            helper = switcher.get(constraint[0].lower(), lambda: print("Invalid constraint."))
            newClauses = helper(self.s.toIndex(constraint[1]), self.s.toIndex(constraint[2]))
            self.clauses = self.clauses + newClauses
        # Adding clauses already in CNF form.
        self.clauses = self.clauses + self.s.getCNFConstraints()

        for clause in self.clauses:
            #print(clause)
            #print([abs(clause[i]) for i in range(len(clause))])
            #print([features[abs(clause[i])] for i in range(len(clause))])
            self.solver.add(Or([features[clause[i]] for i in range(len(clause))]))

        return features

    def createObjectives(self):
        obj = Int("objective")
        self.solver.add(obj>0)
        return obj

    def createPath(self, initState, finalState):
        self.solver.pop()

        for f in initState:
            pass

        #add contraints on transitions

        self.solver.minimize(self.objective)
        print(self.solver.check())  # prints sat
        print(self.solver.model())  # prints [x = 4]


models = "../data/RIS-FOP/"
s = SystemData(featuresFile=models + 'features.txt')
oracle = OracleSolver(s, states=1)
oracle.createPath([], [])