class Refinement:
    def __init__(self, arrayCopy, systemData, mode="Normal", writeMode=False, evolution=None):
        if len(arrayCopy) == 0:
            print('No test case found.')
            return
        self.testSuite = self.orderArray(arrayCopy.copy(), systemData.getContexts(), evolution.getNumberPrevTests())
        self.systemData = systemData
        self.mode = mode
        self.writeMode = writeMode
        self.evolution = evolution

    def printTestSuite(self):
        print("========== RESULTS =============")
        features = self.systemData.getFeatures()
        contexts = self.systemData.getContexts()


    def printRefinedTestCase(testCase, nTest, contexts, features, prevTestCase, newNodes=None):
        if newNodes is None:
            newNodes = contexts + features
        newLine = str(nTest) + ' || DELETED CONTEXTS : '
        newLine += str([context for context in testCase if
                        testCase[context] < 0 and context in contexts and prevTestCase[
                            context] > 0 and context in newNodes])
        newLine += '\n  || ADDED CONTEXTS : '
        newLine += str([context for context in testCase if
                        testCase[context] > 0 and context in contexts and prevTestCase[
                            context] < 0 and context in newNodes])
        newLine += '\n  || DELETED FEATURES : '
        newLine += str([feature for feature in testCase if
                        testCase[feature] < 0 and feature in features and prevTestCase[
                            feature] > 0 and feature in newNodes])
        newLine += '\n  || ADDED FEATURES : '
        newLine += str([feature for feature in testCase if
                        testCase[feature] > 0 and feature in features and prevTestCase[
                            feature] < 0 and feature in newNodes])
        print(newLine)
        print(
            '---------------------------------------------------------------------------------------------------------')

    """ Sorts the array thanks to the distance definition in testDistance.
    """

    def orderArray(self, testSuite, nodes, nPrevTests):
        prevTest = []
        newArray = []
        prevTest = []
        if nPrevTests > 0:
            for i in range(nPrevTests):
                prevTest = self.testSuite[0]
                newArray.append(prevTest)
                self.testSuite.remove(prevTest)
        else:
            prevTest = min(testSuite, key=lambda testCase: sum([testCase[c] for c in nodes]))
            newArray = [prevTest]
            testSuite.remove(prevTest)

        while testSuite:  # until all test cases are transferred
            prevTest = min(testSuite, key=lambda testCase: self.testDistance(testCase, prevTest, nodes))
            newArray.append(prevTest)
            testSuite.remove(prevTest)
        return newArray
        # array = sorted(array, key=lambda testCase: testCaseDistance(testCase, initialTest))

    """Returns the distance between t1 and t2, only for features/contexts contained in nodes.
    """

    def testDistance(self, t1, t2, nodes=None):
        distance = 0
        for node in t1:
            if t1[node] != t2[node]:
                if nodes is None or node in nodes:
                    distance += 1
        return distance

    def parentConstraint(self, constraints, root):
        concernedConstraints = []
        for constraint in constraints:
            (_, p, _) = constraint
            if p == root:
                concernedConstraints.append(constraint)
        if len(concernedConstraints) == 0:
            return None
        return concernedConstraints