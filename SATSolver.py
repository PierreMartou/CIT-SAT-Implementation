from pysat.solvers import Glucose3
from ConstraintsToCNF import *


class SATSolver:
    def __init__(self, systemData):
        self.systemData = systemData
        if self.systemData is None:
            print("No data provided. Impossible to model a SAT solver.")

        self.solver = Glucose3(incr=True)

        self.clauses = []
        for constraint in self.systemData.getConstraints():
            helper = switcher.get(constraint[0].lower(), lambda: print("Invalid constraint."))
            newClauses = helper(self.systemData.toIndex(constraint[1]), self.systemData.toIndex(constraint[2]))
            self.clauses = self.clauses + newClauses

        for clause in self.clauses:
            self.solver.add_clause(clause)

        if not self.checkSAT([]):
            raise AssertionError("This model is not solvable.")

    def printClauses(self):
        for clause in self.clauses:
            toPrint = []
            for literal in clause:
                if literal<0:
                    toPrint.append('- ' + self.systemData.getNodes()[abs(literal)])
                else:
                    toPrint.append(self.systemData.getNodes()[abs(literal)])
            print(toPrint)

    def checkSAT(self, values=None):
        if values is None:
            values = []
        return self.solver.solve(assumptions=values)

    def getModel(self):
        return self.solver.get_model()

    def propagate(self, values=None):
        if values is None:
            values = []
        return self.solver.propagate(assumptions=values)

