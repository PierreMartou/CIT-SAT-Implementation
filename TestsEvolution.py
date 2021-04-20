import random
from SATSolver import SATSolver
from ResultRefining import orderArray

class TestsEvolution:
    def __init__(self, testFile, systemData, mode):
        self.newNodes = []
        self.augmentedTests = []
        self.prevTests = []
        self.initDefinedTests(testFile)
        self.systemData = systemData
        self.mySolver = SATSolver(systemData)
        self.nPrevTests = 0
        self.mode = mode
        # Suppose every previous test is correct

    def augmentTests(self):
        actualNodes = self.systemData.getNodes()
        self.newNodes = [node for node in actualNodes if node not in self.prevNodes and node is not "dummy"]
        self.updateIndexes()
        if self.mode is "SAT":
            self.augmentTestsWithSAT()
        elif self.mode is "CIT":
            self.augmentTestsWithCIT()
        else:
            for line in self.mode:
                augmentedTests = self.augmentTestsWithConstraints(line)
                self.prevTests = augmentedTests
            # At this point, the features are normally all completed.
            self.augmentTestsWithSAT()

    def augmentTestsWithSAT(self):
        nTests = 0
        rawAugmentedTestCases = []
        for testCase in self.prevTests:
            sat = self.mySolver.checkSAT(testCase.values())
            if sat is False:
                print("Hypothesis violated : a previous test case is not solvable anymore.")
            else:
                rawAugmentedTestCases.append(self.mySolver.getModel())
                nTests += 1

        self.augmentedTests = self.testCasesToNodes(rawAugmentedTestCases)
        self.nPrevTests = nTests

    def augmentTestsWithConstraints(self, line):
        scenarios = []
        decipheredMode = line.split("/")
        constraint = decipheredMode[1].lower()
        features = decipheredMode[2].split("-")
        #pseudo code:
        # test code/dead features beforehand
        # create scenarios (CIT)
        # sort scenarios with sorting algorithm
        # combine scenarios greedy way until it works

        # scenario algo : per feature relationship, generate a predefined covering array (O(log(n)) in terms of new features
        # to generate with CIT SAT
        if constraint in ["mandatory"]:
            scenarios.append([self.systemData.toIndex(features[0])])  # not generalized at all
            scenarios.append([-self.systemData.toIndex(features[0])])
        elif constraint in ["or", "optional", "alternative"]:
            zero_scenar = {}
            for f in features:
                zero_scenar[f] = -self.systemData.toIndex(f)
            scenarios.append(zero_scenar)
            for feature in features:
                zero_temp = zero_scenar.copy()
                zero_temp[feature] = self.systemData.toIndex(feature)
                scenarios.append(zero_temp)

            if constraint not in ["alternative"]:
                full_scenar = {}
                for f in features:
                    full_scenar[f] = self.systemData.toIndex(f)
                scenarios.append(full_scenar)

        randomMode = False
        if randomMode:
            index = [i for i in range(len(scenarios))]
            random.shuffle(index)
            shuffledScenarios = [scenarios[i] for i in index]
            scenarios = shuffledScenarios
        else:
            scenarios = orderArray(scenarios, scenarios[0].keys())
        self.nPrevTests = len(self.prevTests)
        segmentLength = self.nPrevTests / len(scenarios) / 2
        #barriers = [n*quartersLength for n in range(1, 2*len(scenarios))]
        #barriers.append(self.nPrevTests)
        yoyoNumbers = list(range(0, len(scenarios))) + list(range(len(scenarios)-2, -1, -1))
        #assignedScenario = []
        #lastBarrier = 0
        #scenarioNumber = 0
        #for b in barriers:
        #    for i in range(lastBarrier, round(b)):
        #        assignedScenario.append(scenarioNumber)
        #    scenarioNumber += 1
        #    lastBarrier = round(b)
        currentTestCase = 0
        finalAssignedScenario = []
        # validation; if it doesn't work try to yo-yo and find another; if it doesn't work just SAT.getmodel() and it's a new scenario
        newAugmentedTests = []
        timeLeft = segmentLength
        currentScenario = 0
        for testCase in self.prevTests:
            print(timeLeft)
            if timeLeft < 0:
                currentScenario = (currentScenario + 1)%len(scenarios)
                timeLeft = segmentLength
            exploredScenario = currentScenario
            sat = False
            while not sat:
                augmentedTestCase = testCase.copy()

                for f in scenarios[exploredScenario]:
                    augmentedTestCase[f] = scenarios[exploredScenario][f]

                sat = self.mySolver.checkSAT(augmentedTestCase.values())

                if sat:
                    newAugmentedTests.append(augmentedTestCase)
                    if exploredScenario != currentScenario:
                        currentScenario = exploredScenario
                        print("Had to change the base scenario.")
                        timeLeft = segmentLength
                    else:
                        timeLeft -= 1
                    finalAssignedScenario.append(exploredScenario)
                    currentTestCase += 1

                if not sat:
                    exploredScenario = (currentScenario + 1)%len(scenarios)

        print(finalAssignedScenario)
        return newAugmentedTests

    def updateIndexes(self):
        convertedTests = []
        indexForFeatures = self.systemData.getValuesForFactors()
        for testCase in self.prevTests:
            convertedTestCase = {}
            for node in self.prevNodes:
                index = indexForFeatures[node][0]
                if node in testCase:
                    convertedTestCase[node] = index
                else:
                    convertedTestCase[node] = -int(index)
            convertedTests.append(convertedTestCase)
        self.prevTests = convertedTests

    def testCasesToNodes(self, convertedTests):
        augmentedTests = []
        finalNodes = self.systemData.getNodes()
        for convertedTestCase in convertedTests:
            testCase = {}
            for index in convertedTestCase:
                testCase[finalNodes[abs(index)]] = index
            augmentedTests.append(testCase)
        return augmentedTests

    def getAugmentedTests(self):
        return self.augmentedTests.copy()

    def getNumberPrevTests(self):
        return self.nPrevTests

    def getNewNodes(self):
        return self.newNodes

    def initDefinedTests(self, testFile):
        if testFile is None:
            print("No previous tests defined.")
            self.prevTests = []
        else:
            f = open(testFile, "r").readlines()
            self.prevTests = []
            self.prevNodes = f[0].split("-")[:-1]
            self.nPrevTests = len(f[1:])
            for line in f[1:]:
                parsedLine = line.split("-")[:-1]
                self.prevTests = self.prevTests + [parsedLine]

    def augmentTestsWithCIT(self):
        pass

