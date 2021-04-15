import random
from ResultRefining import orderArray

class TestsEvolution:
    def __init__(self, testFile, systemData, mySolver, mode):
        self.newNodes = []
        self.augmentedTests = []
        self.prevTests = []
        self.initDefinedTests(testFile)
        self.systemData = systemData
        self.mySolver = mySolver
        self.nPrevTests = 0
        self.mode = mode
        # Suppose every previous test is correct

    def augmentTests(self):
        actualNodes = self.systemData.getNodes()
        self.newNodes = [node for node in actualNodes if node not in self.prevNodes and node is not "dummy"]
        if self.mode is "SAT":
            self.augmentTestsWithSAT()
        elif self.mode is "CIT":
            self.augmentTestsWithCIT()
        else:
            for line in self.mode:
                self.augmentTestsWithConstraints(line)

    def augmentTestsWithSAT(self):
        nTests = 0
        convertedTestCases = self.testCasesToIndex()
        rawAugmentedTestCases = []
        for testCase in convertedTestCases:
            sat = self.mySolver.checkSAT(testCase.values())
            if sat is False:
                print("Hypothesis violated : a previous test case is not solvable anymore.")
            else:
                rawAugmentedTestCases.append(self.mySolver.getModel())
                nTests += 1

        self.augmentedTests = self.testCasesToNodes(rawAugmentedTestCases)
        self.nPrevTests = nTests

    def augmentTestsWithConstraints(self, line):
        nTests = 0
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

        randomMode = True
        if randomMode:
            index = [i for i in range(len(scenarios))]
            random.shuffle(index)  #
            shuffledScenarios = [scenarios[i] for i in index]
            scenarios = shuffledScenarios
        else:
            scenarios = orderArray(scenarios, scenarios[0].keys())
        self.nPrevTests = len(self.testCasesToIndex())
        quartersLength = self.nPrevTests / len(scenarios)
        barriers = [n*quartersLength for n in range(1, len(scenarios))]
        barriers.append(self.nPrevTests)
        scenarioNumbers = self.getScenarioNumbers(scenarios)
        assignedScenario = []
        lastBarrier = 0
        scenarioNumber = 0
        for b in barriers:
            for i in range(lastBarrier, round(b)):
                assignedScenario.append(scenarioNumber)
            scenarioNumber += 1
            lastBarrier = round(b)
        currentTestCase = 0
        # validation; if it doesn't work try to yo-yo and find another; if it doesn't work just SAT.getmodel() and it's a new scenario
        for testCase in self.testCasesToIndex():
            augmentedTestCase = testCase.copy()
            currentScenario = assignedScenario[currentTestCase]
            for iprime in range(currentScenario, currentScenario+len(scenarios)):
                augmentedTestCase.update(scenarios[iprime])
                if self.mySolver.checkSAT(augmentedTestCase.values()):
                    self.augmentedTests.append(augmentedTestCase)
                    currentScenario = iprime
                    assignedScenario = [a if a != currentScenario else iprime for a in assignedScenario]
            currentTestCase += 1


    def getScenarioNumbers(self, scenarios):
        scenarioNumbers = [i for i in range(len(scenarios))]
        tmp = scenarioNumbers.copy()
        tmp.reverse()
        scenarioNumbers = scenarioNumbers + tmp
        return scenarioNumbers

    def testCasesToIndex(self):
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
        return convertedTests

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

