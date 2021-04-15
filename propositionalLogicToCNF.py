class Literal:
    def __init__(self, number, sign):
        self.number = number * sign
        self.sign = sign

    def getNumber(self):
        return self.number

    def alternateSign(self):
        self.number = -self.number
        self.sign = -self.sign

    def getSign(self):
        return self.sign

    def distributeOR(self):
        return True

class Clause:
    def __init__(self, connective, literals, sign):
        if connective not in ["OR", "AND"]:
            print("Clause not defined with OR or AND, given type was : " + str(connective))

        self.connective = connective

        for literal in literals:
            if type(literal) is not Literal and type(literal) is not Clause:
                print("The members of the cell were not either a String or another Cell.")

        self.literals = literals
        self.sign = sign

    def getConnective(self):
        return self.connective

    def getLiterals(self):
        return self.literals

    def isBasicCell(self):
        for lit in self.literals:
            if type(lit) is not Literal:
                return False
        return True

    def alternateSign(self):
        self.sign = - self.sign
        self.moveNegativeInwards()

    def moveNegativeInwards(self):
        if self.sign < 0:
            for lit in self.literals:
                lit.alternateSign()

    def mergeClauses(self):
        newLiterals = []
        for lit in self.literals:
            if type(lit) is not Clause:
                newLiterals.append(lit)
            else:
                lit.mergeClauses()
                if lit.getConnective == self.connective:
                    newLiterals.extend(lit.getLiterals())
                else:
                    newLiterals.append(lit)

    def distributeOR(self):
        self.mergeClauses()
        if self.connective == "AND":
            for lit in self.literals:
                continueLoop = lit.distributeOR()
                #TODO end here
                self.mergeClauses()

        if self.connective == "OR" and not self.isBasicCell():
            for lit in self.literals:
                if type(lit) is Clause: # then this Clause is AND, because self is currently OR and we merged clause
                    pass #TODO end here

def convertToCNF(propositionalLogicExpression):
    propositionalLogicExpression.moveNegativeInwards()

    propositionalLogicExpression.mergeClauses()

    # make first clause "AND"


def isCNF(clause):
    if clause.getType() != "AND":
        return False
    for lit in clause.getLiterals():
        if type(lit) is not Clause or lit.getConnective() is not "OR" or not lit.isBasicCell():
            return False
    return True


