import random
from SATSolver import SATSolver
from TestsEvolution import TestsEvolution
"""A set is under the form ((feature1, _), (feature2, _)).
orderedSet returns the set with feature1 and feature2 ordered like in the keys of valuesForFactors.
"""
def orderedSet(set, valuesForFactors):

    factors = list(valuesForFactors)
    if factors.index(set[0][0]) < factors.index(set[1][0]):
        return set
    else:
        return [set[1], set[0]]

""" Select the next best factor-value pair, which has the most uncovered sets.
Breaks tie randomly.
"""
def selectBestPair(unCovPairsCount):
    bestScore = max(unCovPairsCount.values())
    candidates = [key for key, value in unCovPairsCount.items() if value == bestScore]
    return random.choice(candidates)

""" Select the best value for a specific factor (= that would cover the most uncompleted t-sets), 
considering a partial test case 
"""
def selectSpecificBestValue(f, valuesForFactors, unCovSets, currentTestCase):
    candidates = []
    bestScore = -1
    for v in valuesForFactors[f]:
        pair = (f, v)
        score = 0
        possibleSets = [orderedSet([pair, (testFactor, currentTestCase[testFactor])], valuesForFactors) for testFactor in currentTestCase]
        for set in possibleSets:
            if set in unCovSets:
                score += 1
        if score > bestScore:
            bestScore = score
            candidates = [v]
        elif score == bestScore:
            candidates.append(v)
    return random.choice(candidates)


""" Select the best test case in the test case pool (= which would cover the most uncovered sets) """
def selectBestTestCase(testCasePool, valuesForFactors, unCovSets):
    if len(testCasePool) == 0:
        return []
    candidates = []
    bestScore = -1
    for testCase in testCasePool:
        score = computeSetCoverScore(testCase, valuesForFactors, unCovSets)
        if score > bestScore:
            bestScore = score
            candidates = [testCase]
        elif score == bestScore:
            candidates.append(testCase)
    return random.choice(candidates)


""" Computes how many sets that test case would cover if it was added to the covering array, among the uncovered sets. """
def computeSetCoverScore(testCase, valuesForFactor, unCovSets):
    possibleSets = []
    score = 0
    factors = list(valuesForFactor.keys())
    for i1 in range(len(factors)-1):
        pair1 = (factors[i1], testCase[factors[i1]])
        for i2 in range(i1+1, len(factors)):
            pair2 = (factors[i2], testCase[factors[i2]])
            possibleSets.append([pair1, pair2])
    for set in possibleSets:
        if set in unCovSets:
            score += 1
    return score


# valuesForFactor is important here, as it sets the order of factors in sets : (f1, f2) is not the same set as (f2, f1), which does not exist as all sets are ordered
def updateUnCovSets(testCase, valuesForFactor, unCovSets, unCovPairsCount):
    factors = list(valuesForFactor.keys())
    for i1 in range(len(factors) - 1):
        pair1 = (factors[i1], testCase[factors[i1]])
        for i2 in range(i1 + 1, len(factors)):
            pair2 = (factors[i2], testCase[factors[i2]])
            if [pair1, pair2] in unCovSets:
                unCovSets.remove([pair1, pair2])
                unCovPairsCount[pair1] = max(0, unCovPairsCount[pair1]-1)
                unCovPairsCount[pair2] = max(0, unCovPairsCount[pair2] - 1)

    return unCovSets, unCovPairsCount

"""Computes every possible pair in valuesForFactors, but removes those not compatible with the SAT solver"""
def computeSetToCover(valuesForFactors, SATSolver=None):
    unCovSets = []
    unCovPairsCount = {}
    factors = list(valuesForFactors.keys())
    for i in range(len(factors) - 1):
        for j in range(len(valuesForFactors[factors[i]])):
            pair1 = (factors[i], valuesForFactors[factors[i]][j])
            for i2 in range(i + 1, len(factors)):
                for j2 in range(len(valuesForFactors[factors[i2]])):
                    pair2 = (factors[i2], valuesForFactors[factors[i2]][j2])

                    if SATSolver == None or SATSolver.checkSAT([pair1[1], pair2[1]]):
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
    return unCovSets, unCovPairsCount

def discoverCore(solver, valuesForFactors):
    core = {}
    for factor in valuesForFactors:
        if not solver.checkSAT([valuesForFactors[factor][1]]):
            core[factor] = valuesForFactors[factor][0]
    return core

"""Main algorithm of this module. Implementation of a greedy CIT-SAT algorithm, and returns a covering array."""
def CITSAT(systemData, verbose=False, numCandidates=20, testsEvolution = None):
    mySATsolver = SATSolver(systemData)
    valuesForFactors = systemData.getValuesForFactors()

    core = discoverCore(mySATsolver, valuesForFactors)
    useCore = True
    propagate = True
    if useCore:
        for key in core.keys():
            del valuesForFactors[key]
    coveringArray = []
    numTests = 0
    numPropagation = 0
    numPropagatedNodes = 0
    # generating T-sets and helpful T-set counts
    unCovSets, unCovPairsCount = computeSetToCover(valuesForFactors, mySATsolver)
    uncoveredTSetCount = len(unCovSets)
    factors = list(valuesForFactors.keys())
    if verbose:
        print("Finished computing covering sets.")
    nPrevTestCases = 0
    if testsEvolution is not None:
        testsEvolution.augmentTests()
        for testCase in testsEvolution.getAugmentedTests():
            nPrevTestCases += 1
            numTests += 1
            coveringArray.append(testCase)
            if verbose:
                print("Prev test case added : ")
                print(testCase)
            unCovSets, unCovPairsCount = updateUnCovSets(testCase, valuesForFactors, unCovSets, unCovPairsCount)
            uncoveredTSetCount = len(unCovSets)

    while uncoveredTSetCount > 0:
        testCasePool = []
        for count in range(numCandidates):
            newTestCase = {}
            bestFactor, bestValue = selectBestPair(unCovPairsCount)  # the factor-value that has the most of t-sets left to cover
            newTestCase[bestFactor] = bestValue
            if propagate:
                numPropagation += 1
                prevNumberOfValues = len(newTestCase.keys())
                (_, newValues) = mySATsolver.propagate(newTestCase.values())
                finalNodes = systemData.getNodes()
                for value in newValues:
                    newTestCase[finalNodes[abs(value)]] = value
                numPropagatedNodes += len(newTestCase.values()) - prevNumberOfValues

            shuffledRemainingFactors = [f for f in factors if f != bestFactor]
            random.shuffle(shuffledRemainingFactors)  # shuffles randomly the remaining factor
            for f in shuffledRemainingFactors:
                if f in newTestCase:
                    continue
                augmentedNewTestCase = newTestCase
                v = selectSpecificBestValue(f, valuesForFactors, unCovSets, augmentedNewTestCase)
                augmentedNewTestCase[f] = v
                sat = mySATsolver is None or mySATsolver.checkSAT(augmentedNewTestCase.values())
                if not sat:
                    augmentedNewTestCase[f] = -v

                #PROPAGATION PHASE ?
                if propagate:
                    numPropagation += 1
                    prevNumberOfValues = len(augmentedNewTestCase.keys())
                    (_, newValues) = mySATsolver.propagate(augmentedNewTestCase.values())
                    finalNodes = systemData.getNodes()
                    for value in newValues:
                        augmentedNewTestCase[finalNodes[abs(value)]] = value
                    numPropagatedNodes += len(augmentedNewTestCase.values()) - prevNumberOfValues
                    #print("Propagated " + str(len(augmentedNewTestCase.values()) - prevNumberOfValues) + " new values.")
                    #if len(augmentedNewTestCase.values()) - prevNumberOfValues == 0:
                        #print(f)
                newTestCase = augmentedNewTestCase

            # Orders the keys in the dictionary; useless but pretty to the eyes when printed
            orderedNewTestCase = dict.fromkeys(systemData.getValuesForFactors())
            for key in orderedNewTestCase:
                if not useCore:
                    orderedNewTestCase[key] = newTestCase[key]
                else:
                    if key in core:
                        orderedNewTestCase[key] = core[key]
                    else:
                        orderedNewTestCase[key] = newTestCase[key]
            testCasePool.append(orderedNewTestCase)

        if len(testCasePool) > 0:
            bestTestCase = selectBestTestCase(testCasePool, valuesForFactors, unCovSets)
            coveringArray.append(bestTestCase)
            if verbose:
                print("Test case added : ")
                print(bestTestCase)
            unCovSets, unCovPairsCount = updateUnCovSets(bestTestCase, valuesForFactors, unCovSets, unCovPairsCount)
            uncoveredTSetCount = len(unCovSets)
            numTests += 1

    if propagate:
        print("EFFICIENCY OF THE PROPAGATION")
        print("PROPAGATIONS : " + str(numPropagation) + " - PROP  NODES : " + str(numPropagatedNodes) + " - AVERAGE : " + str(numPropagatedNodes/max(1,numPropagation)))
    return coveringArray


def CITSATForAugmentation(systemData, testsEvolution):
    pass