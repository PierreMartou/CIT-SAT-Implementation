"""
from CITSAT
def selectGenericBestValue(f, valuesForFactors, unCovPairsCount):
    candidates = []
    bestScore = -1
    for v in valuesForFactors[f]:
        pair = (f, v)
        if unCovPairsCount(pair) > bestScore:
            bestScore = unCovPairsCount(pair)
            candidates = [pair]
        elif unCovPairsCount(pair) == bestScore:
            candidates.append(pair)
    return random.choice(candidates)"""

"""ResultRefining
def printCoveringArray(array):
    print("========== RESULTS =============")
    if len(array) == 0:
        print('No test case found.')
        return

    nTabsNeeded = {}
    headline = ''
    for feature in array[0]:
        headline += '|' + feature
        length = len(feature)
        print(length)
        nTabsNeeded[feature] = int((length)/8)+1
        for i in range(4-nTabsNeeded[feature]):
            headline += '\t'

    print(headline)

    for testCase in array:
        newLine = ''
        for feature in testCase:
            newLine += '|' + str(testCase[feature]) + '\t\t\t\t'
        print(newLine)"""



"""In Result refining

def orderNodes(constraints, root):
    newNodes = [root]
    relatedConstraints = parentConstraint(constraints, root)
    if relatedConstraints is None:
        return newNodes
    else:
        for constraint in relatedConstraints:
            for child in constraint[2]:
                newNodes += orderNodes(constraints, child)
    return newNodes
"""


"""in plots.py
def testAETG():
    valuesForFactors = {}
    valuesForFactors['F1'] = [1, 2]
    valuesForFactors['F2'] = [3, 4, 5]
    valuesForFactors['F3'] = [5, 6, 7]
    result = AETG(valuesForFactors)
    printCoveringArray(result)


def testAETGWithFeatures():
    s = SATSolver("features-list.txt")
    result = CITSAT(s, None, False)
    printCoveringArray(result)

def testAETGWithContextsAndMapping():
    s = SATSolver(featureFile="features-list.txt", mappingFile="mapping.txt", contextsFile="contexts-list.txt")
    result = CITSAT(s, None, False)
    printCoveringArray(result, s, False)
    print("================================Change Mode=====================================")
    printCoveringArray(result, s, True)

def testSATLibrary():
    g = Glucose3()
    g.add_clause([-1, 2])
    g.add_clause([-2, 3])

    print(g.solve())
    print(g.solve(assumptions=[1]))
    print(g.solve(assumptions=[2]))
    print(g.solve(assumptions=[-3]))
    print(g.get_model())
"""
