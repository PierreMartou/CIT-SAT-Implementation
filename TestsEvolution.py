import random
from SATSolver import SATSolver
from ResultRefining import orderArray

class TestsEvolution:
    def __init__(self, testFile, systemData, mode):
        self.newNodes = []
        self.augmentedTests = []
        self.prevTests = []
        self.systemData = systemData
        self.initDefinedTests(testFile)
        self.mySolver = SATSolver(systemData)
        self.nPrevTests = 0
        self.mode = mode
        self.augmentTests()
        # Suppose every previous test is correct

    def augmentTests(self):
        actualNodes = self.systemData.getNodes()
        self.newNodes = [node for node in actualNodes if node not in self.prevNodes and node is not "dummy"]
        if self.mode is "SAT":
            self.augmentTestsWithSAT()
        elif self.mode is "1to2" or self.mode is "2to3":
            self.augmentTestsWithCodedFeat()
            self.augmentTestsWithSAT()
        elif type(self.mode) is int:
            step = self.mode
            self.mode = "2to3"
            self.augmentTestsWithCodedFeat(step)
            self.augmentTestsWithSAT()
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
        queue = []
        for s in scenarios:
            queue.append(s)
        finalAssignedScenario = []
        newAugmentedTests = []
        timeLeft = round(segmentLength)

        sat = True
        currentScenario = queue[0]
        queue.remove(currentScenario)
        queue.append(currentScenario)

        while len(self.prevTests) != 0:
            if timeLeft == 0 or not sat:
                currentScenario = queue[0]
                queue.remove(currentScenario)
                queue.append(currentScenario)
                timeLeft = round(segmentLength)

            augmentedTestCase = self.prevTests[0].copy()
            for f in currentScenario:
                augmentedTestCase[f] = currentScenario

            sat = self.mySolver.checkSAT(augmentedTestCase.values())

            if sat:
                newAugmentedTests.append(augmentedTestCase)
                self.prevTests = self.prevTests[1:]
                timeLeft -= 1
                finalAssignedScenario.append(currentScenario)
        # print(finalAssignedScenario)
        self.prevTests = newAugmentedTests

    def transformToIndexes(self):
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
            if type(testFile) is str:
                f = open(testFile, "r").readlines()
                self.prevTests = []
                self.prevNodes = f[0].split("-")[:-1]
                self.nPrevTests = len(f[1:])
                for line in f[1:]:
                    parsedLine = line.split("-")[:-1]
                    self.prevTests = self.prevTests + [parsedLine]
                self.transformToIndexes()
            else:
                self.prevNodes = testFile[0][1:].copy()
                myPrevTests = testFile[1]
                self.prevTests = myPrevTests.copy()
                self.nPrevTests = len(testFile[1])

                convertedTests = []
                for testCase in self.prevTests:
                    convertedTestCase = {}
                    for node in self.prevNodes:
                        if testCase[node] > 0:
                            convertedTestCase[node] = self.systemData.valuesForFactors[node][0]
                        else:
                            convertedTestCase[node] = self.systemData.valuesForFactors[node][1]
                    convertedTests.append(convertedTestCase)
                self.prevTests = convertedTests

    def augmentTestsWithCodedFeat(self, step=None):
        scenarios = []
        if type(self.systemData.toIndex("Minimalist")) is int:
            self.mode = "2to3"
        else:
            self.mode = "1to2"

        if self.mode in "1to2":
            scenarios.append([self.systemData.toIndex("Match")])
            scenarios.append([self.systemData.toIndex("Search")])
        elif self.mode in "2to3":
            scenarios.append([self.systemData.toIndex("Minimalist")])
            scenarios.append([self.systemData.toIndex("Minimalist"), self.systemData.toIndex("Keyboard")])
            scenarios.append([self.systemData.toIndex("Complete"), self.systemData.toIndex("Keyboard")])
            scenarios.append([self.systemData.toIndex("Complete")])
            scenarios.append([self.systemData.toIndex("Keyboard")])
        self.nPrevTests = len(self.prevTests)
        segmentLength = self.nPrevTests / len(scenarios) / 2
        queue = []
        for s in scenarios:
            queue.append(s)
        finalAssignedScenario = []
        newAugmentedTests = []

        if step is None:
            step = round(segmentLength)
        timeLeft = step
        sat = True
        currentScenario = queue[0]
        queue.remove(currentScenario)
        queue.append(currentScenario)
        while len(self.prevTests) != 0:
            if timeLeft == 0 or not sat:
                currentScenario = queue[0]
                queue.remove(currentScenario)
                queue.append(currentScenario)
                timeLeft = step

            augmentedTestCase = self.prevTests[0].copy()
            if not self.mySolver.checkSAT(augmentedTestCase.values()):
                print("a test case was found invalid")
                return newAugmentedTests
            for f in currentScenario:
                node = self.systemData.getNodes()[f]
                augmentedTestCase[node] = f

            sat = self.mySolver.checkSAT(augmentedTestCase.values())
            if sat:
                newAugmentedTests.append(augmentedTestCase)
                self.prevTests.remove(self.prevTests[0])
                timeLeft -= 1
                finalAssignedScenario.append(currentScenario)
        # print("Assigned scenarios : " + str(finalAssignedScenario))
        self.prevTests = newAugmentedTests


