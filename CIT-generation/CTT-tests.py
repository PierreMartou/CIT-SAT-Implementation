from CTT import greedyCTT
from TestSuite import *
from CTTheuristics import BuildingCTT
import os
import numpy as np


def computeCTTSuite(fpath, iteration, s, interaction_filter=True, weight_lookahead=0.5, weight_comparative=0.5, recompute=False):
    filepath = fpath + str(iteration)+".pkl"
    if os.path.exists(filepath) and not recompute:
        testSuite = readSuite(filepath)
    else:
        t = BuildingCTT(s, verbose=False, numCandidates=30, interaction_filter=interaction_filter, weight_lookahead=weight_lookahead, weight_comparative=weight_comparative)
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


def graphCoverageEvolution(iterations):
    models = "../data/RIS-FOP/"
    s = SystemData(featuresFile=models+'features.txt')
    allSize = []
    allInteractionEvolution = []
    allTransitionEvolution = []
    mode = 0
    storage = "../data/RIS-FOP/TestSuitesCTT-" + str(mode) + "/testSuite"
    for i in range(iterations):
        i_filter = False
        w_la = 0
        w_c = 0
        if mode >= 1:
            i_filter = True
        if mode >= 2:
            w_la = 0.5
        if mode >= 3:
            w_c = 0.5

        testSuite = computeCTTSuite(storage, i, s, interaction_filter=i_filter, weight_lookahead=w_la, weight_comparative=w_c)
        allSize.append(testSuite.getLength())
        interactionEvolution, transitionEvolution = testSuite.interactionTransitionCoverageEvolution()
        allInteractionEvolution.append(interactionEvolution)
        allTransitionEvolution.append(transitionEvolution)

    sizeAverage = sum(allSize) / len(allSize)
    sizeVariance = np.var(allSize)
    interactionEvolutionAverage = []

    """y1 =
    x = np.linspace(1, len(y)+1, num=len(y), endpoint=True)
    xnew = np.linspace(1, len(y)+1, num=41, endpoint=True)
    param = polyfit(x, y, 2)
    f = polyval(param, xnew)

    font = {'family': 'normal',
            'size': 16}
    plt.rc('font', **font)

    plt.plot(x, y, 'o', xnew, f, '--')
    plt.legend(['Data', 'Least square approximation'])
    plt.title('')
    plt.xlabel('S')
    plt.ylabel('Total cost')
    #test = [1, 3, 5, 7, 9, 11, 13, 15]
    #plt.xticks(test, test)
    plt.savefig("results/totalCost.pdf")
    plt.show()"""


"""def singleSuite():
    models = "../data/RIS/"
    storage = "../data/RIS/TestSuitesCTT/testSuite/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    testSuite = computeCTTSuite(storage, 0, s, recompute=True)
    testSuite.printLatexTransitionForm(mode="unordered")
"""

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
