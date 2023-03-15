from SATSolver import SATSolver
import time
import random


class BuildingCTT:
    def __init__(self, systemData, verbose, numCandidates=30):
        self.systemData = systemData
        self.solver = SATSolver(systemData)
        self.valuesForFactors = systemData.getValuesForFactors()
        self.core = self.discoverCore()
        for key in self.core.keys():
            del self.valuesForFactors[key]

        self.coveringArray = []
        numTests = 0
        self.unCovSets, self.unCovTransitions, self.unCovPairsCount = self.computeSetToCoverBasicHeuristics()
        self.factors = list(self.valuesForFactors.keys())

        while len(self.unCovSets) + len(self.unCovTransitions) > 0:
            testCasePool = []
            prevTestCase = None if len(self.coveringArray) == 0 else self.coveringArray[-1]
            for count in range(numCandidates):
                # Add first pair of factor-value to the test case.
                newTestCase = {}
                pairsScores = self.computeScores(prevTestCase, "basic")
                bestScore = max(pairsScores.values())
                bestFactor, bestValue = random.choice([key for key, value in pairsScores.items() if value == bestScore])
                newTestCase[bestFactor] = bestValue

                # Propagate this value using the SATsolver to find associated values.
                newTestCase = self.propagateCurrentTestCase(newTestCase)

                # Find a value for all other context and feature, in a random order.
                shuffledRemainingFactors = [f for f in self.factors if f not in newTestCase]
                random.shuffle(shuffledRemainingFactors)
                for f in shuffledRemainingFactors:
                    v = self.selectSpecificBestValue(f, newTestCase, prevTestCase)
                    newTestCase[f] = v
                    if not self.solver.checkSAT(newTestCase.values()):
                        newTestCase[f] = -v

                    # Propagate new values.
                    newTestCase = self.propagateCurrentTestCase(newTestCase)

                # Once the test case is built, this orders the keys in the dictionary; useless but pretty to the eyes when printed.
                orderedNewTestCase = dict.fromkeys(systemData.getValuesForFactors())
                # Adds the core values for a complete test case.
                for key in orderedNewTestCase:
                    if key in self.core:
                        orderedNewTestCase[key] = self.core[key]
                    else:
                        orderedNewTestCase[key] = newTestCase[key]
                testCasePool.append(orderedNewTestCase)

            # Selects the best test case among all candidates.
            if len(testCasePool) > 0:
                bestTestCase = self.selectBestTestCase(testCasePool, prevTestCase, "basic")
                self.coveringArray.append(bestTestCase)
                self.updateUnCovSets(bestTestCase, prevTestCase)
                numTests += 1

    def computeScores(self, prevTestCase, heuristics="basic"):
        tempUnCovPairsCount = self.unCovPairsCount.copy()
        for transition in self.unCovTransitions:
            if prevTestCase is None or transition[0][1] == prevTestCase[transition[0][0]] or transition[1][1] == prevTestCase[transition[1][0]]:
                tempUnCovPairsCount[transition[0]] = tempUnCovPairsCount[transition[0]] - 1
                tempUnCovPairsCount[transition[1]] = tempUnCovPairsCount[transition[1]] - 1

        # ADD HEURISTICS HERE. NULL SCORES FOR DUPLICATES IN CIT; LOOKAHEAD SCORES.
        # REFACTOR : scores[(factor, value)] = computeScore(f, v, currentTestCase={}, prevTestCase, heuristics)

        return tempUnCovPairsCount

    def selectSpecificBestValue(self, f, currentTestCase, prevTestCase, heuristics="basic"):
        candidates = []
        bestScore = -1
        for v in self.valuesForFactors[f]:
            pair = (f, v)
            score = 0
            possibleInteractions = [self.orderedSet([pair, (testFactor, currentTestCase[testFactor])])
                                    for testFactor in currentTestCase]
            possibleTransitions = []
            if prevTestCase is not None and prevTestCase[f] != v:
                possibleTransitions = [self.orderedSet([pair, (otherF, currentTestCase[otherF])])
                                       for otherF in currentTestCase if currentTestCase[otherF] != prevTestCase[otherF]]
            for interaction in possibleInteractions:
                if interaction in self.unCovSets:
                    score += 1
            for transition in possibleTransitions:
                if transition in self.unCovTransitions:
                    score += 1
            if score > bestScore:
                bestScore = score
                candidates = [v]
            elif score == bestScore:
                candidates.append(v)
        return random.choice(candidates)

    def selectBestTestCase(self, testCasePool, prevTestCase, heuristics="basic"):
        candidates = []
        bestScore = -1
        for testCase in testCasePool:
            possibleInteractions = self.computeAllPairs(testCase)
            possibleTransitions = []
            if prevTestCase is not None:
                possibleTransitions = [pair for pair in possibleInteractions if prevTestCase[pair[0][0]] != pair[0][1] and prevTestCase[pair[1][0]] != pair[1][1]]

            # ADD HEURISTICS HERE.
            score = 0
            for set in possibleInteractions:
                if set in self.unCovSets:
                    score += 1
            for transition in possibleTransitions:
                if transition in self.unCovTransitions:
                    score += 1
            if score > bestScore:
                bestScore = score
                candidates = [testCase]
            elif score == bestScore:
                candidates.append(testCase)
        return random.choice(candidates)

    def updateUnCovSets(self, testCase, prevTestCase):
        possibleInteractions = self.computeAllPairs(testCase)
        possibleTransitions = []
        if prevTestCase is not None:
            possibleTransitions = [pair for pair in possibleInteractions if prevTestCase[pair[0][0]] != pair[0][1] and prevTestCase[pair[1][0]] != pair[1][1]]
        for set in possibleInteractions:
            if set in self.unCovSets:
                self.unCovSets.remove(set)
                self.unCovPairsCount[set[0]] = self.unCovPairsCount[set[0]] - 1
                self.unCovPairsCount[set[1]] = self.unCovPairsCount[set[1]] - 1
                if self.unCovPairsCount[set[0]] < 0 or self.unCovPairsCount[set[1]] < 0:
                    print("PROBLEM IN UPDATEUNCOVSETS; SETS")

        for transition in possibleTransitions:
            if transition in self.unCovTransitions:
                self.unCovTransitions.remove(transition)
                self.unCovPairsCount[transition[0]] = self.unCovPairsCount[transition[0]] - 1
                self.unCovPairsCount[transition[1]] = self.unCovPairsCount[transition[1]] - 1
                if self.unCovPairsCount[transition[0]] < 0 or self.unCovPairsCount[transition[1]] < 0:
                    print("PROBLEM IN UPDATEUNCOVSETS; TRANSITIONS")

    def computeAllPairs(self, testCase):
        possibleSets = []
        for i in range(len(self.factors)-1):
            pair1 = (self.factors[i], testCase[self.factors[i]])
            for j in range(i+1, len(self.factors)):
                pair2 = (self.factors[j], testCase[self.factors[j]])
                possibleSets.append([pair1, pair2])
        return possibleSets

    """A set is under the form ((feature1, _), (feature2, _)).
    orderedSet returns the set with feature1 and feature2 ordered like in the keys of valuesForFactors.
    """
    def orderedSet(self, interaction):
        if self.factors.index(interaction[0][0]) < self.factors.index(interaction[1][0]):
            return interaction
        else:
            return [interaction[1], interaction[0]]

    def propagateCurrentTestCase(self, newTestCase):
        (_, newValues) = self.solver.propagate(newTestCase.values())
        finalNodes = self.systemData.getNodes()
        for value in newValues:
            newTestCase[finalNodes[abs(value)]] = value
        return newTestCase

    def discoverCore(self):
        core = {}
        for factor in self.valuesForFactors:
            if not self.solver.checkSAT([self.valuesForFactors[factor][1]]):
                core[factor] = self.valuesForFactors[factor][0]
        return core

    """Computes every possible pair in valuesForFactors, but removes those not compatible with the SAT solver"""
    def computeSetToCoverBasicHeuristics(self):
        unCovSets = []
        unCovTransitions = []
        unCovPairsCount = {}
        factors = list(self.valuesForFactors.keys())
        for i in range(len(factors) - 1):
            for j in range(len(self.valuesForFactors[factors[i]])):
                pair1 = (factors[i], self.valuesForFactors[factors[i]][j])
                for i2 in range(i + 1, len(factors)):
                    for j2 in range(len(self.valuesForFactors[factors[i2]])):
                        pair2 = (factors[i2], self.valuesForFactors[factors[i2]][j2])

                        if self.solver.checkSAT([pair1[1], pair2[1]]):
                            # Each set is a [Factor, Value, Factor, Value, ...] tuple
                            unCovSets.append([pair1, pair2])
                            if pair1 not in unCovPairsCount:
                                unCovPairsCount[pair1] = 1
                            else:
                                unCovPairsCount[pair1] += 1

                            if pair2 not in unCovPairsCount:
                                unCovPairsCount[pair2] = 1
                            else:
                                unCovPairsCount[pair2] += 1
                            if self.solver.checkSAT([-1*pair1[1], -1*pair2[1]]):
                                unCovTransitions.append([pair1, pair2])
                                unCovPairsCount[pair1] += 1
                                unCovPairsCount[pair2] += 1
        return unCovSets, unCovTransitions, unCovPairsCount

    def getCoveringArray(self):
        return self.coveringArray.copy()