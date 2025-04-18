from utils.TestSuite import *
from TestOracle.AlternativePaths import computeAlts
from metrics.CTTmetrics import getNumberOfSPLOTModels, smoothLinearApprox, computeCorrelation
import matplotlib.pyplot as plt

from TestOracle.TestOracleExecutioner.TestController import EmergencyController
from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner

"""models = "../data/RIS-FOP/"
features = models + 'features.txt'
suite_storage = models + "TestSuitesCTT/"
alt_suite_storage = models + "AlternativePaths/alts"
testsuite = computeCTTSuite(suite_storage, features, iteration=1, recompute=False, verbose=True)
testsuite.printLatexTransitionForm()
paths, undetectables = computeAlts(alt_suite_storage, features, testsuite.getUnorderedTestSuite(), tag=0, states=4, recompute=False)

lengthAndCost = [t.getShortenedLengthAndCost() for p in paths for t in p]
averageNumberOfPaths = sum([len(p) for p in paths]) / len(paths)
totalStates = sum([t[0] - 2 for t in lengthAndCost])
averageLength = totalStates / len(lengthAndCost)
totalCost = sum([t[1] for t in lengthAndCost])
averageCost = totalCost / len(lengthAndCost)
print("number of groups of paths is", len(paths), ", average number of paths is", averageNumberOfPaths,
      "their length is on average ", averageLength, "their cost is on average", averageCost)
print("total number of states is", totalStates, "total cost is", totalCost)"""

controller = EmergencyController()
reference = 0
skip_generation = False
TestingToolRunner.launch_test_oracle(controller, "./", "./features.txt", skip_generation, reference)
