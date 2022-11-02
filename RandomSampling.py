from SATSolver import SATSolver
import random


def randomTestCase(valuesForFactors, satSolver):
    features = list(valuesForFactors.keys())
    random.shuffle(features)
    testCase = {}
    for f in features:
        testCase[f] = random.choice(valuesForFactors[f])
        sat = satSolver.checkSAT(testCase.values())
        if not sat:
            testCase[f] = -testCase[f]
    return testCase


def randomSampling(systemData):
    mySATsolver = SATSolver(systemData)
    valuesForFactors = systemData.getValuesForFactors()
    testSuite = []
    for i in range(18):
        newTestCase = randomTestCase(valuesForFactors, mySATsolver)
        testSuite.append(newTestCase)
    return testSuite


def computeCoverage(pairs, testSuite):
    coverPairsCount = 0
    for pair in pairs:
        if containsPair(pair, testSuite):
            coverPairsCount += 1
    return coverPairsCount


def containsPair(pair, testSuite):
    f1 = pair[0][0]
    v1 = pair[0][1]
    f2 = pair[1][0]
    v2 = pair[1][1]
    for testCase in testSuite:
        if testCase[f1] == v1 and testCase[f2] == v2:
            return True
    return False

def allPairs(systemData, filtered=True):
    mySATsolver = SATSolver(systemData)
    valuesForFactors = systemData.getValuesForFactors()
    unCovSets = []
    factors = list(valuesForFactors.keys())
    for i in range(len(factors) - 1):
        for j in range(len(valuesForFactors[factors[i]])):
            pair1 = (factors[i], valuesForFactors[factors[i]][j])
            for i2 in range(i + 1, len(factors)):
                for j2 in range(len(valuesForFactors[factors[i2]])):
                    pair2 = (factors[i2], valuesForFactors[factors[i2]][j2])

                    if mySATsolver.checkSAT([pair1[1], pair2[1]]):
                        # Each set is a [Factor, Value, Factor, Value, ...] tuple
                        unCovSets.append([pair1, pair2])
    if filtered:
        cores = []
        for candidate in list(valuesForFactors.keys()):
            if not mySATsolver.checkSAT([-1*abs(valuesForFactors[candidate][0])]):
                cores.append(candidate)
        unCovSets = [unCovSet for unCovSet in unCovSets if unCovSet[0][0] not in cores and unCovSet[1][0] not in cores]
    return unCovSets


def invalidChance(systemData):
    valuesForFactors = systemData.getValuesForFactors()
    mySatSolver = SATSolver(systemData)
    iterations = 1000000
    score = 0
    for i in range(iterations):
        testCase = {}
        for f in valuesForFactors:
            testCase[f] = random.choice(valuesForFactors[f])
        if mySatSolver.checkSAT(testCase.values()):
            score += 1
    print(str(iterations) + " test cases, "+ str(score) + " valid cases.")
