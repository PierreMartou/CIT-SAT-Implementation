import os
from utils.TestSuite import *
from ErrorIsolation import *
from TestOracle.AlternativePaths import computeAlts, retrieveAlts

from TestOracle import AlternativePaths
import sys
import utils


from metrics.CTTmetrics import getNumberOfSPLOTModels, smoothLinearApprox, computeCorrelation
import matplotlib.pyplot as plt
from TestOracle.TestOracleExecutioner.TestController import EmergencyController
from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner


"""controller = EmergencyController()
reference = 0
skip_generation = False
testing_tool_folder = "./"
feature_model_path = "./features.txt"
discrepancies = TestingToolRunner.launch_test_oracle(controller, testing_tool_folder, feature_model_path, skip_generation, reference)
discr = discrepancies[0]
print("Discrepancy found:", discr)
culprits = error_isolation(controller, testing_tool_folder, feature_model_path, discr[1], reference, discr[0], verbose=True)
print(culprits)
#testing_z3solver(feature_model_path)"""


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



def initialisation_isolation_metrics(max_iterations=5):
    modelFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txt/"
    constraintsFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txtconstraints/"
    storageCTT = "../data/SPLOT/SPLOT-NEW/SPLOT-TestSuitesCTT/"
    storageAlts = "../data/SPLOT/SPLOT-NEW/SPLOT-Alts/"

    nb_groups = {}
    step = 1

    for filename in os.listdir(modelFiles):
        txt = os.path.join(modelFiles, filename)
        txtConstraints = os.path.join(constraintsFiles, filename)
        s = SystemData(featuresFile=txt, extraConstraints=txtConstraints)

        nb_features = len(s.getFeatures())

        tempStorageCTT = storageCTT + filename[:-4] + "-1&2&3-"
        """for iteration in range(max_iterations):
            print("\rComputing model " + str(quty) + "/" + str(total), iteration + 1, "/", max_iterations,
                  " (category: " + str(rangeCategory) + "), model " + str(filename), flush=True, end='')"""
        iteration = 0
        original_suite = computeCTTSuite(tempStorageCTT, s, iteration, recompute=False)

        tempstorageAlts = storageAlts + filename[:-4]
        paths, undetectable = retrieveAlts(tempstorageAlts)

        suspects = find_suspects_SPLOT(original_suite, paths, step)

        result = []
        return

        for iteration in range(max_iterations):
            result.append(group_initialisation(find_suspects(original_path, alt_path, 0), s))

        result = sum(result)/max_iterations

        if nb_features in nb_groups:
            nb_groups[nb_features] = nb_groups[nb_features] + [result]
        else:
            nb_groups[nb_features] = [result]

    print(nb_groups)


sys.modules['AlternativePaths'] = AlternativePaths
sys.modules['SystemData'] = utils.SystemData
sys.modules['TestSuite'] = utils.TestSuite
initialisation_isolation_metrics()