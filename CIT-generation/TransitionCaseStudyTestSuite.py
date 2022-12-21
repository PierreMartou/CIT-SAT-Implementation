import os
import time

from TestSuiteCostComparisons import *

def findSuitableCITsuite(s, errors, verbose = False, stats = False,  mode="random"):
    valid = False
    countValids = 0
    testSuite = "truc"
    maxIterations = 100
    iteration = 0
    while not valid and iteration < maxIterations:
        iteration += 1
        result = CITSAT(s)
        testSuite = TestSuite(s, result)
        transitions = testSuite.transitionPairCoverage(mode)
        valid = True
        for e in errors:
            if e in transitions or (e[1], e[0]) in transitions:
                valid = False
        if valid:
            countValids += 1
        if stats:
            valid = False
    if iteration == maxIterations:
        print("Max iterations reached.")
        if stats:
            print("(mode = "+str(mode)+") On " + str(maxIterations), " iterations, there was " + str(countValids) + " test suites with the corresponding transitions.")
    elif verbose:
        print("Found after " + str(iteration) + " iterations.")
        printCoveringArray(testSuite.getRandomTestSuite(), s, mode="Refined", latex=False)
    return testSuite


models = "../data/RiS/"
s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
testSuite = findSuitableCITsuite(s, [("+Instructions", "-Map"), ("+lowRisk", "-highRisk")], stats=True)

testSuite = findSuitableCITsuite(s, [("+lowRisk", "-highRisk")], stats=True, mode="unordered")


# printCoveringArray(testSuite.getMinTestSuite(), s, mode="Refined", latex=False)
# transitions = testSuite.transitionPairCoverageMinimised()
# for t in transitions:
#    print(t)

# Errors are:
# 1)Transition error, UI error : +Instructions -Map (upperA will be below instead of above). Not found by CIT.
# 2) Transition error, message-based error : +lowRisk-highRisk (counter will be at 0 instead of 1). Not found by CIT.
# 3) Interaction error, UI error :
