from TestOracle.OracleSolver import OracleSolver
from utils.SystemData import SystemData
from utils.SATSolver import SATSolver
from utils.TestSuite import allTransitions
import pickle
import os
import sys

def computeAlts(fpath, s, testSuite, iteration=0, states=6, recompute=False, verbose=False):
    version = "1.2.0"
    filepath = fpath + "-" + str(states) + ".pkl"

    if not isinstance(s, SystemData):
        s = SystemData(featuresFile=s)

    if os.path.exists(filepath) and not recompute:
        alts = readAlts(filepath)
        if not alts.isUpToDate(version):
            #print("Alt paths not up to date, regenerating, for file: ", fpath)
            alts = AlternativePaths(s, states, version, verbose=verbose)
    else:
        #print("Recomputing paths for file: ", fpath)
        alts = AlternativePaths(s, states, version, verbose=verbose)

    if alts.computedTestSuite(iteration):
        return alts.altPathsForTestSuite(testSuite, iteration=iteration)
    else:
        #print("Unknown tag, recomputing paths for file: ", fpath)
        toReturn = alts.altPathsForTestSuite(testSuite, iteration=iteration)
        storeAlts(alts, filepath)
        return toReturn


def retrieveAlts(fpath, tag=0, states=4):
    filepath = fpath + "-" + str(states) + ".pkl"
    if os.path.exists(filepath):
        alts = readAlts(filepath)
    else:
        return None

    if alts.computedTestSuite(tag):
        return alts.altPathsForTestSuite(None, tag=tag)
    else:
        return None


def readAlts(filePath):
    alts = pickle.load(open(filePath, 'rb'))
    return alts

def storeAlts(alts, filePath):

    f = open(filePath, "wb")
    pickle.dump(alts, f)
    f.close()


class AlternativePaths:
    def __init__(self, systemData, states=4, version="1.0.0", verbose=False):
        self.version = version
        self.verbose = verbose
        self.s = systemData
        self.states = states
        self.allTransitions = allTransitions(self.s)
        self.decomposableTransitions = None
        self.nonDecomposableTransitions = None
        self.allResults = {}

    def isUpToDate(self, version):
        if hasattr(self, "version"):
           return self.version == version
        return False

    def computedTestSuite(self, tag):
        return tag in self.allResults

    def preprocessTransitions(self, solver):
        decomposables = []
        nonDecomposables = []
        for t in self.allTransitions:
            #indexedT = [self.s.toIndex(f[1:]) if f[0:1] == '+' else -self.s.toIndex(f[1:]) for f in t]
            if self.decomposableTransition(solver, t):
                decomposables.append(t)
            else:
                nonDecomposables.append(t)
        return decomposables, nonDecomposables

    def decomposableTransition(self, solver, transition):
        values = []
        for i in range(len(transition)):
            for j in range(len(transition)):
                f = transition[j]
                values.append(f[1] if i != j else -1 * f[1])
            if solver.checkSAT(values):
                return True
        return False


    def altPathsForTestSuite(self, testSuite, iteration=0):
        if iteration in self.allResults:
            return self.allResults[iteration][0], self.allResults[iteration][1]

        solver = OracleSolver(self.s, self.states, timeout=10000)

        satSolver = SATSolver(self.s)
        self.decomposableTransitions, self.nonDecomposableTransitions = self.preprocessTransitions(satSolver)

        transitionsToCover = self.decomposableTransitions if self.decomposableTransitions is not None else self.allTransitions
        totalTransitions = len(transitionsToCover)
        allUncoverablesTransitions = self.nonDecomposableTransitions if self.nonDecomposableTransitions is not None else []
        allPaths = []
        if self.decomposableTransitions is not None:
            transitionsToCover = self.decomposableTransitions
        transitionsToCover = [self.simplifiedTransition(t) for t in transitionsToCover]
        if self.verbose:
            print("Progression: 0%", end='')

        for i in range(len(testSuite)-1):
            #if len(transitionsToCover) == 0:
            #    print("Transition complete before end of test suite is abnormal. Error.")
            #    return None
            if self.verbose:
                print("\rProgression: ", round((i/len(testSuite))*100, 2), "%", flush=True, end='')
            newPaths, transitionsToCover, uncoverableTransitions = self.createAlternativePaths(testSuite[i], testSuite[i+1], transitionsToCover, solver)
            allUncoverablesTransitions = allUncoverablesTransitions + uncoverableTransitions
            allPaths.append(newPaths)
        if self.verbose:
            print("\rProgression: ", 100, "%  ", flush=True)

        if totalTransitions > 0:
            undetectables = len(allUncoverablesTransitions)/totalTransitions
        else:
            undetectables = 0
        self.allResults[iteration] = allPaths, undetectables
        return allPaths, undetectables

    def createAlternativePaths(self, config1, config2, transitionsToCover, solver, prevUncoverables = []):
        #algo for branching off paths
        changes = [(f, config2[f]) for f in config1 if config1[f] != config2[f]]
        possibleCoverage = []
        for i in range(len(changes)-1):
            for j in range(i+1, len(changes)):
                t = self.simplifiedTransition((changes[i], changes[j]))
                if t in transitionsToCover:
                    possibleCoverage.append(t)
        if len(possibleCoverage) == 0:
            return [], transitionsToCover, []
        possiblePathCoverage = [possibleCoverage]
        currentCoverage = []
        uncoverableTransitions = []
        paths = []
        while len(possiblePathCoverage) > 0:
            possibleCoverage = possiblePathCoverage.pop()
            #print("computing new path", possibleCoverage)
            path = solver.createPath(config1, config2, possibleCoverage)
            if path is None:
                #print("failed to create a path")
                if len(possibleCoverage) > 1:
                    possiblePathCoverage.append(possibleCoverage[:round(len(possibleCoverage)/2)])
                    possiblePathCoverage.append(possibleCoverage[round(len(possibleCoverage)/2):])
                else:
                    uncoverableTransitions.append(possibleCoverage[0])
                    transitionsToCover.remove(possibleCoverage[0])
            else:
                paths.append(path)
                for t in possibleCoverage:
                    currentCoverage.append(t)

        if len(uncoverableTransitions) == 0:
            for t in currentCoverage:
                transitionsToCover.remove(t)
            return paths, transitionsToCover, prevUncoverables
        else:
            return self.createAlternativePaths(config1, config2, transitionsToCover, solver, prevUncoverables=prevUncoverables+uncoverableTransitions)

    def getNondecomposableTransitions(self):
        return self.nonDecomposableTransitions.copy()

    def getDecomposableTransitions(self):
        return self.decomposableTransitions.copy()

    def simplifiedTransition(self, transition):
        orderedTransition = transition
        if transition[0][0] < transition[1][0]:
            orderedTransition = (transition[1], transition[0])
        value0 = 1 if orderedTransition[0][1] > 0 else -1
        value1 = 1 if orderedTransition[1][1] > 0 else -1
        simplifiedTransition = ((orderedTransition[0][0], value0), (orderedTransition[1][0], value1))
        return simplifiedTransition
