from CTT import greedyCTT
from TestSuiteCostComparisons import *
from CTTheuristics import BuildingCTT
import os


def computeCTTSuite(fpath, iteration, s, recompute=False):
    filepath = fpath + str(iteration)+".pkl"
    if os.path.exists(filepath) and not recompute:
        testSuite = readSuite(filepath)
    else:
        t = BuildingCTT(s, verbose=True, numCandidates=30)
        testSuite = TestSuite(s, t.getCoveringArray())
        storeSuite(testSuite, filepath)
    return testSuite


def computeCITSuite(fpath, iteration, s, recompute=False):
    filepath = fpath + str(iteration)+".pkl"
    if os.path.exists(filepath) and not recompute:
        testSuite = readSuite(filepath)
    else:
        testSuite = TestSuite(s, CITSAT(s, False, 30))
        storeSuite(testSuite, filepath)
    return testSuite


def singleSuite():
    models = "../data/RIS/"
    storage = "../data/RIS/TestSuitesCTT/testSuite/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    testSuite = computeCTTSuite(storage, 0, s, recompute=True)
    testSuite.printLatexTransitionForm(mode="unordered")


def SPLOTresults():
    model = "../data/SPLOT/SPLOT-txt/model_20110516_1331478109.txt"
    storage = "../data/SPLOT/SPLOT-TestSuites/"
    s = SystemData(None, model, None)
    testSuite = computeCTTSuite(storage, 0, s, recompute=False)
    testSuite.printLatexTransitionForm(mode="unordered")

def getCITcoverage():
    model = "../data/SPLOT/SPLOT-txt/model_20110516_1331478109.txt"
    storage = "../data/SPLOT/SPLOT-TestSuitesCIT/"
    s = SystemData(None, model, None)
    testSuite = computeCITSuite(storage, 0, s)
    testSuite.printLatexTransitionForm(mode="unordered")


#SPLOTresults()
getCITcoverage()
