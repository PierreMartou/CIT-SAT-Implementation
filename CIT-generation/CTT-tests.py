from CTT import greedyCTT
from TestSuiteCostComparisons import *
import os

def computeCTTSuite(iteration, s):
    filepath = "../data/RIS/TestSuitesCTT/testSuite"+str(iteration)+".pkl"
    if os.path.exists(filepath):
        testSuite = readSuite(filepath)
    else:
        testSuite = TestSuite(s, greedyCTT(s))
        storeSuite(testSuite, filepath)
    return testSuite


def singleSuite():
    models = "../data/RIS/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    testSuite = computeCTTSuite(0, s)
    testSuite.printLatexTransitionForm(mode="unordered")


singleSuite()