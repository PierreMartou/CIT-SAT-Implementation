import os
import time

from TestSuiteCostComparisons import *

def allTransitions(pairs, s, filterForFeatures=True):
    transitions = []
    for i in range(len(pairs)):
        pair = pairs[i]
        if filterForFeatures and (pair[0][0] not in s.getFeatures() or pair[1][0] not in s.getFeatures()):
            continue
        if findReversePair(pair, pairs):
            firstTransition = "+" if pair[0][1] > 0 else "-"
            firstTransition += pair[0][0]
            secondTransition = "+" if pair[1][1] > 0 else "-"
            secondTransition += pair[1][0]
            transitions.append((firstTransition, secondTransition))
    return transitions


def findReversePair(pair, pairs):
    for p in pairs:
        if p[0][1] == -1 * pair[0][1] and p[1][1] == -1 * pair[1][1]:
            return True
    return False


def computeTestSuite(iteration):
    filepath = "../data/RIS/TestSuitesComplete/testSuite"+str(iteration)+".pkl"
    if os.path.exists(filepath):
        testSuite = readSuite(filepath)
    else:
        testSuite = TestSuite(s, CITSAT(s))
        storeSuite(testSuite, filepath)
    return testSuite


def findSuitableCITsuite(s, errors, search="stats", mode="random", verbose=True):
    countValids = 0
    averageErrorFounds = 0
    maxIterations = 1000
    normalise = maxIterations / 100
    iteration = 0
    while iteration < maxIterations:
        iteration += 1
        testSuite = computeTestSuite(iteration)
        transitions = testSuite.transitionPairCoverage(mode)

        contains = True
        errorFound = len(errors)
        for e in errors:
            if e not in transitions and (e[1], e[0]) not in transitions:
                contains = False
                errorFound -= 1
        averageErrorFounds += errorFound/len(errors)
        if contains:
            countValids += 1
        if not contains and search == "notContains":
            print("Found after " + str(iteration) + " iterations.")
            printCoveringArray(testSuite.getRandomTestSuite(), s, mode="Refined", latex=False)
            return testSuite
        elif contains and search == "contains":
            print("Found after " + str(iteration) + " iterations.")
            printCoveringArray(testSuite.getRandomTestSuite(), s, mode="Refined", latex=False)
            return testSuite
    # print("Max iterations reached.")
    percentage = round(countValids/normalise, 2)
    if verbose:
        print("mode = "+str(mode) + " : " + str(percentage) + " % containing the transitions.")
    if search == "statsContain":
        return percentage
    elif search == "statsCoverage":
        return averageErrorFounds/maxIterations
    print("MODE NOT RECOGNIZED")


models = "../data/RiS/"
s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')

modes = ["unordered", "random", "dissimilarity", "minimized"]
"""print("-HIGH +LOW")
for mode in modes:
    findSuitableCITsuite(s, [("-High", "+Low")], search="statsContain", mode=mode)

print("-MAP +INSTRUCTIONS")
for mode in modes:
    findSuitableCITsuite(s, [("+Instructions", "-Map")], search="statsContain", mode=mode)

print("TWO TRANSITIONS")
for mode in modes:
    findSuitableCITsuite(s, [("-High", "+Low"), ("+Instructions", "-Map")], search="statsContain", mode=mode)

print("+HIGH +INSTRUCTIONSFLOODS")
for mode in modes:
    findSuitableCITsuite(s, [("+InstructionsFloods", "+High")], search="statsContain", mode=mode)"""

allPairs = allPairs(s)
allTransitions = allTransitions(allPairs, s)
print("Computing chance of finding a specific transition in a suite.")
"""percentages = [0, 0, 0, 0]
it = 5
for transition in allTransitions[0:it]:
    for mode in modes:
        percentages[modes.index(mode)] += findSuitableCITsuite(s, [transition], search="statsContain", mode=mode, verbose=False)
percentages = [p/it for p in percentages]
print("Averages: " + str(percentages))"""

print("Computing percentage of coverage in average.")
av = 50
percentages = [0, 0, 0, 0]
it = 50
print(allTransitions[0:it])
for mode in modes:
    percentages[modes.index(mode)] += findSuitableCITsuite(s, [allTransitions[0:it]], search="statsCoverage", mode=mode, verbose=False)
print("Average: " + str(percentages))
# printCoveringArray(testSuite.getMinTestSuite(), s, mode="Refined", latex=False)
# transitions = testSuite.transitionPairCoverageMinimised()
# for t in transitions:
#    print(t)

# Errors are:
# 1) Transition error, UI error : -Map +Instructions (upperA will be below instead of above).
# 2) Transition error, message-based error : -high+low (counter will be at 0 instead of 1).
# 3) Interaction error, error : +InstructionsColdWeather +InstructionsFloods
