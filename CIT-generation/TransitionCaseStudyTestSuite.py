import os
import time

from TestSuiteCostComparisons import *

def findSuitableCITsuite(s, errors):
    valid = False
    testSuite = "truc"
    while not valid:
        result = CITSAT(s)
        testSuite = TestSuite(s, result)
        transitions = testSuite.transitionPairCoverageMinimised()
        valid = True
        for e in errors:
            if e in transitions or (e[1], e[0]) in transitions:
                valid = False
    return testSuite


models = "../data/RiS/"
s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
testSuite = findSuitableCITsuite(s, [("+Instructions", "-Map"), ("+lowRisk", "-highRisk")])
printCoveringArray(testSuite.getMinTestSuite(), s, mode="Refined", latex=False)

# printCoveringArray(testSuite.getMinTestSuite(), s, mode="Refined", latex=False)
# transitions = testSuite.transitionPairCoverageMinimised()
# for t in transitions:
#    print(t)

# Errors are:
# 1)Transition error, UI error : +Instructions -Map (upperA will be below instead of above). Not found by CIT.
# 2) Transition error, message-based error : +lowRisk-highRisk (counter will be at 0 instead of 1). Not found by CIT.
# 3) Interaction error, UI error :
