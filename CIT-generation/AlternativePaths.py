from OracleSolver import OracleSolver
from TestSuite import allTransitions
from CITSAT import orderedSet
class AlternativePaths:
    def __init__(self, systemData, states=3):
        self.s = systemData
        self.states = states
        self.solver = OracleSolver(systemData, states)
        self.allTransitions = allTransitions(self.s)
        self.decomposableTransitions, self.nonDecomposableTransitions = self.solver.preprocessTransitions(self.allTransitions)

    def altPathsForTestSuite(self, testSuite):
        coveredTransitions = []
        allPaths = []
        for i in range(len(testSuite)-1):
            newPaths, coveredTransitions = self.createAlternativePaths(testSuite[i], testSuite[i+1], coveredTransitions)
            allPaths.append(newPaths)
            if len(coveredTransitions) == len(self.decomposableTransitions):
                print("Transition complete before end of test suite is abnormal. Error.")
                return None
        return allPaths, coveredTransitions

    def createAlternativePaths(self, config1, config2, coveredTransitions):
        #algo for branching off paths
        changes = [(f, config2[f]) for f in config1 if config1[f] != config2[f]]
        possibleCoverage = []
        for i in range(len(changes)-1):
            for j in range(i+1, len(changes)):
                t = orderedSet((changes[i], changes[j]), self.s.getValuesForFactors())
                if t not in coveredTransitions:
                    possibleCoverage.append(t)
        if len(possibleCoverage) == 0:
            return [], coveredTransitions
        possiblePathCoverage = [possibleCoverage]
        uncoverableTransitions = []
        paths = []
        while len(possiblePathCoverage) > 0:
            possibleCoverage = possiblePathCoverage.pop()
            path = self.solver.createPath(config1, config2, possibleCoverage)
            if path is None:
                if len(possibleCoverage) > 1:
                    possiblePathCoverage.append(possibleCoverage[:round(len(possibleCoverage)/2)])
                    possiblePathCoverage.append(possibleCoverage[round(len(possibleCoverage)/2):])
                else:
                    print("does it ever happen ?", possibleCoverage)
                    uncoverableTransitions.append(possibleCoverage[0])
            else:
                paths.append(path)
                for t in possibleCoverage:
                    coveredTransitions.append(t)

        return paths, coveredTransitions

    def getNondecomposableTransitions(self):
        return self.nonDecomposableTransitions.copy()

    def getDecomposableTransitions(self):
        return self.decomposableTransitions.copy()
