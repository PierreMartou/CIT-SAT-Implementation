from OracleSolver import OracleSolver
from SystemData import SystemData
from TestSuite import *
from AlternativePaths import AlternativePaths


def metrics():
    models = "../data/RIS-FOP/"
    s = SystemData(featuresFile=models + 'features.txt')
    storage = models + "TestSuitesCTT/testSuite" + str("1&2&3") + "-"
    suite = computeCTTSuite(storage, 0, s, recompute=True).getMinTestSuite()
    #print(suite)
    states = 2
    alts = AlternativePaths(s, states)
    paths, coveredTransitions = alts.altPathsForTestSuite(suite)
    print("paths :", paths)
    print("len coverage :", len(coveredTransitions))
    print("len undecomposable :", len(alts.getNondecomposableTransitions()), "vs len decomposable :", len(alts.getDecomposableTransitions()))

    #oracle = OracleSolver(s, states)
    #testSuite = oracle.createPath(suite[0], suite[1])
    #if testSuite is not None:
    #    testSuite = testSuite.getUnorderedTestSuite()
    #    for i in range(len(testSuite)):
    #        print(testSuite[i])

metrics()