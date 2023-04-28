from TestSuite import *
from CTTheuristics import BuildingCTT
from scipy.optimize import curve_fit
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as interpolate

def computeCTTSuite(fpath, iteration, s, interaction_filter=False, weight_lookahead=0, weight_comparative=0, recompute=False):
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


def computeEvolutionAverage(data, iterations):
    evolutionAverage = []
    for evolution in data:
        for i in range(len(evolution)):
            number = evolution[i]
            if i == len(evolutionAverage):
                evolutionAverage.append(100.0-number)
            else:
                evolutionAverage[i] += 100.0-number
    evolutionAverage = [100.0-evolution/iterations for evolution in evolutionAverage]
    return evolutionAverage

def computeSwitchesAverage(data, iterations):
    switchesAverage = []
    for switches in data:
        for i in range(len(switches)):
            number = switches[i]
            if i == len(switchesAverage):
                switchesAverage.append(number)
            else:
                switchesAverage[i] += number
    evolutionAverage = [switches/iterations for switches in switchesAverage]
    return evolutionAverage


def f_log(x, a, b):
    return a * np.log(b * x)


def smoothLinearApprox(x, y):
    x_smooth = np.linspace(min(x), max(x), 500)
    f = interpolate.interp1d(x, y, kind="linear")
    y_smooth = f(x_smooth)
    return x_smooth, y_smooth

def graphCoverageEvolution(iterations, mode=None):
    models = "../data/RIS-FOP/"
    s = SystemData(featuresFile=models+'features.txt')
    font = {'size': 16}
    plt.rc('font', **font)
    label = ["Baseline", "Baseline", "Improvement 1&2", "Improved"]
    lines = ["--", "--", "-", "-"]
    lines2 = ["-.", "-.", ":", ":"]
    linesCoverage = [lines, lines2]
    plot = None
    if mode is None:
        modes = [0, 1, 2, 3]
    else:
        modes = mode

    for mode in modes:
        allSize = []
        allCosts = []
        allInteractionEvolution = []
        allTransitionEvolution = []
        allSwitchesEvolution = []
        w_la = 0
        w_c = 0
        i_filter = False
        if mode >= 1:
            i_filter = True
        if mode >= 2:
            w_la = 0.5
        if mode >= 3:
            w_c = 0.3
        if mode >= 4:
            w_la = 0
        if mode == 5:
            i_filter = False
            w_la = 0.5
            w_c = 0
        storage = models + "TestSuitesCTT/testSuite" + str(mode) + "-"
        for i in range(iterations):
            testSuite = computeCTTSuite(storage, i, s, interaction_filter=i_filter, weight_lookahead=w_la, weight_comparative=w_c, recompute=True)
            allSize.append(testSuite.getLength())
            allCosts.append(testSuite.getCost())
            interactionEvolution, transitionEvolution, switchesEvolution = testSuite.interactionTransitionCoverageEvolution()
            allSwitchesEvolution.append(switchesEvolution)
            allInteractionEvolution.append(interactionEvolution)
            allTransitionEvolution.append(transitionEvolution)

        costAverage = round(sum(allCosts) / len(allCosts), 1)
        costVariance = round(float(np.std(allCosts)), 1)
        print("Mode "+str(mode)+" - Cost average (std deviation): " + str(costAverage) + " (+-" + str(costVariance) + ")")
        sizeAverage = round(sum(allSize) / len(allSize), 1)
        sizeVariance = round(float(np.std(allSize)), 1)
        print("Mode "+str(mode)+" - Size average (std deviation): "+str(sizeAverage) + " (+-" + str(sizeVariance) + ")")
        interactionEvolutionAverage = computeEvolutionAverage(allInteractionEvolution, iterations)
        transitionEvolutionAverage = computeEvolutionAverage(allTransitionEvolution, iterations)
        switchesEvolutionAverage = computeSwitchesAverage(allSwitchesEvolution, iterations)

        cutoffy1 = sum([1 for i in interactionEvolutionAverage if i < 100.0])
        y1 = [0] + interactionEvolutionAverage[:cutoffy1] + [100]

        cutoffy2 = sum([1 for i in transitionEvolutionAverage if i < 100.0])
        y2 = (transitionEvolutionAverage[:cutoffy2])
        y2.append(100)

        switches_cutoff = sum([1 for i in switchesEvolutionAverage if i > 0.05])
        y3 = switchesEvolutionAverage[:switches_cutoff]

        x1 = np.linspace(0, len(y1)+1, num=len(y1))
        x2 = np.linspace(1, len(y2)+1, num=len(y2))
        x3 = np.linspace(1, len(y3)+1, num=len(y3))
        x1_smooth, y1_smooth = smoothLinearApprox(x1, y1)
        x2_smooth, y2_smooth = smoothLinearApprox(x2, y2)
        x3_smooth, y3_smooth = smoothLinearApprox(x3, y3)
        #param1 = np.polyfit(x1, y1, 1)
        #y1_smooth = np.polyval(param1, x_new1)
        #popt = curve_fit(f_log, x1, y1)
        #a1 = popt[0]
        #y1_smooth = [f_log(x, *a1) for x in x_new1]
        #param2 = np.polyfit(x2, y2, 1)
        #y2_smooth = np.polyval(param2, x_new2)
        if plot == 0:
            # font = {'family': 'normal', 'size': 16}
            plt.plot(x1_smooth, y1_smooth, linesCoverage[0][mode], label="Interaction coverage "+label[mode])
            plt.plot(x2_smooth, y2_smooth, linesCoverage[1][mode], label="Transition coverage "+label[mode])
            plt.legend()
            # plt.legend(['interaction coverage', 'transition coverage evolution'])
            # plt.title('Evolution of the interaction/transition coverage of a test suite', fontsize=14)
            plt.xlabel('Test number')
            plt.ylabel('Coverage (%)')
            #test = [1, 3, 5, 7, 9, 11, 13, 15]
            #plt.xticks(test, test)
        elif plot == 1:
            # font = {'family': 'normal', 'size': 16}
            plt.plot(x3_smooth, y3_smooth, lines[mode], label=label[mode])
            plt.legend()
            # plt.legend(['interaction coverage', 'transition coverage evolution'])
            # plt.title('Number of switches in a test suite', fontsize=14)
            plt.xlabel('Test number')
            plt.ylabel('Number of switches')
            #test = [1, 3, 5, 7, 9, 11, 13, 15]
            #plt.xticks(test, test)
    if plot == 0:
        plt.savefig("../results/coverageEvolution.pdf")
    elif plot == 1:
        plt.savefig("../results/switchesEvolution.pdf")
    plt.show()
def getCITSizeAverage(iterations):
    models = "../data/RIS-FOP/"
    s = SystemData(featuresFile=models+'features.txt')
    allSize = []
    allInteractionEvolution = []
    allTransitionEvolution = []
    storage = models + "TestSuitesCIT/testSuite-"
    for i in range(iterations):
        testSuite = computeCITSuite(storage, i, s)
        allSize.append(testSuite.getLength())
        #interactionEvolution, transitionEvolution = testSuite.interactionTransitionCoverageEvolution()
        #allInteractionEvolution.append(interactionEvolution)
        #allTransitionEvolution.append(transitionEvolution)

    sizeAverage = sum(allSize) / len(allSize)
    sizeVariance = np.std(allSize)
    print("Size average (variance) : "+str(sizeAverage) + " (+-" + str(sizeVariance) + ")")


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


def findBestWeights(look_ahead=True):
    models = "../data/RIS-FOP/"
    s = SystemData(featuresFile=models+'features.txt')
    iterations = 200
    values = np.linspace(0, 1, 21)
    print(values)
    sizes = []
    font = {'size': 16}
    plt.rc('font', **font)

    i_filter = True
    w_a = 0.5
    w_c = 0
    for v in values:
        if look_ahead:
            storage = models + "TestSuitesCTT-lookahead/testSuite"+str(round(v, 2))+"-"
        else:
            storage = models + "TestSuitesCTT-comparative/testSuite"+str(round(v, 2))+"-"
        allSize = []
        for i in range(iterations):
            if look_ahead:
                w_a = v
            else:
                w_c = v
            testSuite = computeCTTSuite(storage, i, s, interaction_filter=i_filter, weight_lookahead=w_a, weight_comparative=w_c, recompute=True)
            allSize.append(testSuite.getLength())
        sizes.append(sum(allSize)/len(allSize))
    y1 = sizes
    x1 = values

    x1_smooth, y1_smooth = smoothLinearApprox(x1, y1)

    plt.plot(x1_smooth, y1_smooth, '-')
    if look_ahead:
        plt.xlabel('Look-ahead weight')
    else:
        plt.xlabel('Comparative weight')
    plt.ylabel('Size')
    if look_ahead:
        plt.savefig("../results/look_ahead.pdf")
    else:
        plt.savefig("../results/comparative.pdf")
    plt.show()

# SPLOTresults()
# getCITcoverage()
graphCoverageEvolution(1000, [0, 3])
# findBestWeights(False)
# getCITSizeAverage(50)
