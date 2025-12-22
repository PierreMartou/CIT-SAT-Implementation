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

import numpy as np
from scipy.interpolate import interp1d



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
    storageErrorIsolation = "../data/SPLOT/SPLOT-NEW/SPLOT-ErrorIsolation/default/"

    nb_groups = {}

    average_cost = {}
    average_suspects = {}
    average_steps = {}

    nb_errors = [1, 2, 3]

    quty = 0
    total = getNumberOfSPLOTModels()
    print("Computing model " + "0" + "/" + str(total) + " (category: " + str("all") + ")", flush=True, end='')

    #startpoint = "model_20101117_2128796258.txt"
    startpoint = None
    #startpoint = "model_20110516_1331478109.txt"
    for filename in os.listdir(modelFiles):
        quty += 1
        if startpoint and filename != startpoint:
            continue
        txt = os.path.join(modelFiles, filename)
        txtConstraints = os.path.join(constraintsFiles, filename)
        s = SystemData(featuresFile=txt, extraConstraints=txtConstraints)

        nb_features = len(s.getFeatures())

        tempStorageCTT = storageCTT + filename[:-4] + "-1&2&3-"
        tempstorageAlts = storageAlts + filename[:-4]
        tempStorageErrorIsolation = storageErrorIsolation + filename[:-4]

        """original_suite = computeCTTSuite(storageCTT, s, 0, recompute=False, verbose=False)
        paths, undetectable = computeAlts(tempstorageAlts, s, original_suite)

        lengthAndCost = [t.getShortenedLengthAndCost() for p in paths for t in p]
        # print("Max steps :", max([t[0] - 2 for t in lengthAndCost]), " sum of steps : ", sum([t[0] - 2 for t in lengthAndCost]))
        # averageNumberOfPaths = sum([len(p) for p in paths]) / len(paths)
        steps = sum([t[0] - 2 for t in lengthAndCost])
        cost = sum([t[1] for t in lengthAndCost])
        print("steps : ", steps, "; cost : ", cost)"""

        verbose = False
        curr_nb_groups = 0
        curr_avg_suspects = 0
        #curr_avg_cost = 0
        curr_steps = 0

        error_isolation = getErrorIsolation(tempStorageErrorIsolation, s, tempStorageCTT, tempstorageAlts, verbose=verbose)

        all_suspects = error_isolation.get_all_suspects()
        curr_avg_suspects += sum([len(s) for s in all_suspects]) / len(all_suspects)

        """for iteration in range(max_iterations):
            print("\rComputing model " + str(quty) + "/" + str(total), iteration + 1, "/", max_iterations,
                  " (category: " + str("all, size: ") + str(len(s.getFeatures())) + "), model " + str(filename), flush=True, end='')

            if verbose:
                print("")

            #computedSuite = computeCTTSuite(tempStorageCTT, s, iteration=iteration)
            #curr_avg_cost += computedSuite.getCost()/computedSuite.getLength()

            #paths, undetectable = computeAlts(tempstorageAlts, s, computedSuite, iteration=iteration)
            #alts_cost = []
            #for p in paths:
            #    if len(p) > 0:
            #       alts_cost.append(sum(t.getCost() for t in p)/len(p))

            #curr_avg_cost += sum(alts_cost)/len(alts_cost)

            groups = error_isolation.get_groups(1)

            all_stats = error_isolation.get_all_statistics(nb_errors=[1], states=[10])
            #all_steps = [error_isolation.get_statistics(1, 1, 10)]
            all_steps = []
            for key in all_stats:
                all_steps.append(all_stats[key].steps)
            curr_steps += sum(all_steps)/len(all_steps)

            if groups is not None:
                curr_nb_groups += len(groups)"""


        #curr_statistics

        #average_cost.setdefault(size, []).append(curr_avg_cost / max_iterations)
        average_suspects.setdefault(nb_features, []).append(curr_avg_suspects / max_iterations)
        average_steps.setdefault(nb_features, []).append(curr_steps / max_iterations)

        # print(average_steps)

        result = curr_nb_groups/max_iterations
        if nb_features in nb_groups:
            nb_groups[nb_features] = nb_groups[nb_features] + [result]
        else:
            nb_groups[nb_features] = [result]

    #plot_dict_with_regression(average_cost, "Average number of (de)activations", degree=1)

    average_suspects = aggregate_data(average_suspects)

    r2_score(average_suspects)
    r2_score(average_suspects, degree=1)

    plot_dict_with_regression(average_suspects, "Average number of suspects", degree=1)

def overall_isolation_metrics(max_iterations = 5):
    modelFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txt/"
    constraintsFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txtconstraints/"
    storageCTT = "../data/SPLOT/SPLOT-NEW/SPLOT-TestSuitesCTT/"
    storageAlts = "../data/SPLOT/SPLOT-NEW/SPLOT-Alts/"
    storageErrorIsolation = "../data/SPLOT/SPLOT-NEW/SPLOT-ErrorIsolation/default/"

    all_statistics = {}

    nb_errors = [1, 2, 3]

    quty = 0
    stopping = 300
    total = getNumberOfSPLOTModels()
    print("Computing model " + "0" + "/" + str(total) + " (category: " + str("all") + ")", flush=True, end='')

    for filename in os.listdir(modelFiles):
        quty += 1
        if quty > stopping:
            break
        txt = os.path.join(modelFiles, filename)
        txtConstraints = os.path.join(constraintsFiles, filename)
        s = SystemData(featuresFile=txt, extraConstraints=txtConstraints)

        nb_features = len(s.getFeatures())

        tempStorageCTT = storageCTT + filename[:-4] + "-1&2&3-"
        tempstorageAlts = storageAlts + filename[:-4]
        tempStorageErrorIsolation = storageErrorIsolation + filename[:-4]

        verbose = False
        curr_statistics = ErrorIsolationStatistics()

        error_isolation = getErrorIsolation(tempStorageErrorIsolation, s, tempStorageCTT, tempstorageAlts,
                                            verbose=verbose)

        for iteration in range(max_iterations):
            print("\rComputing model " + str(quty) + "/" + str(total), iteration + 1, "/", max_iterations,
                  " (category: " + str("all, size: ") + str(len(s.getFeatures())) + "), model " + str(filename),
                  flush=True, end='')

            new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=iteration, states=10, recompute=False)

            if new_statistics.divides == 0:
                print("here: ", filename)
            curr_statistics = curr_statistics + new_statistics

        # curr_statistics
        curr_statistics.normalise(max_iterations)
        all_statistics.setdefault(nb_features, []).append(curr_statistics)


    # plot_dict_with_regression(average_cost, "Average number of (de)activations", degree=1)

    all_steps = aggregate_data(all_statistics, key="steps")

    r2_score(all_steps, degree=2)
    r2_score(all_steps, degree=1)

    plot_dict_with_regression(all_steps, "Average number of steps", degree=1)

def MAM_group_metrics(max_iterations=10):
    max_repetitions = 3
    models = "../data/MedicalAppointmentManager/"
    s = SystemData(featuresFile=models + 'features.txt')
    storage = models + "TestSuitesCTT/"
    altsStorage = models + "AlternativePaths/alts"
    normal_storageErrorIsolation = models + "ErrorIsolation/normal/"
    random_storageErrorIsolation = models + "ErrorIsolation/random/"

    normal_statistics = ErrorIsolationStatistics()

    max_groups = 10
    random_statistics = {i: ErrorIsolationStatistics() for i in range(max_groups)}

    print("Computing model MAM, iteration: 0", flush=True, end='')

    for iteration in range(max_iterations):
        print("\rComputing model MAM, iteration: ", iteration, "/", max_iterations, flush=True, end='')

        error_isolation = getErrorIsolation(normal_storageErrorIsolation, s, storage, altsStorage, iteration,
                                            group_mode=None)

        for repetition in range(max_repetitions):
            new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=10,
                                                                    recompute=False)
            normal_statistics += new_statistics

        for i in range(max_groups):
            error_isolation = getErrorIsolation(random_storageErrorIsolation+str(i)+"groups_", s, storage, altsStorage, iteration,
                                                group_mode=i)

            for repetition in range(max_repetitions):
                new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=10,
                                                                        recompute=False)
                random_statistics[i] += new_statistics

    normal_statistics.normalise(max_iterations*max_repetitions)
    for key in random_statistics:
        random_statistics[key].normalise(max_iterations*max_repetitions)

    print(normal_statistics)

    print(random_statistics)

def r2_score(y_true, degree=2):
    print(y_true)
    x = np.array(sorted(y_true.keys()))
    y = np.array([y_true[k] for k in x])

    coeffs = np.polyfit(x, y, deg=degree)
    poly = np.poly1d(coeffs)

    y_hat = poly(x)

    print(y_hat)

    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    r2 = 1 - ss_res / ss_tot

    print(f"(degree {degree}) R² = {r2:.3f}")

def aggregate_data(data, step=10, key=None):
    new_average_suspects = {}
    for i in range(0, 100, step):
        aggregation = []
        for j in range(i, i + step):
            if j in data:
                if key is None:
                    aggregation.extend(data[j])
                else:
                    aggregation.extend(getattr(x, key) for x in data[j])
        if len(aggregation) > 0:
            new_average_suspects[i + 2] = sum(aggregation) / len(aggregation)

    return new_average_suspects

def plot_dict_with_regression(d, label, degree=2):
    # Sort by X
    x = np.array(sorted(d.keys()))
    y = np.array([d[k] for k in x])

    # Scatter points
    plt.scatter(x, y, label=f"Aggregated data")
    if type(degree) == int:
        coeffs = np.polyfit(x, y, deg=degree)
        poly = np.poly1d(coeffs)

        x_dense = np.linspace(x.min(), x.max(), 300)
        y_dense = poly(x_dense)
    elif degree == "exp":
        logy = np.log(y)
        b, loga = np.polyfit(x, logy, deg=1)
        a = np.exp(loga)

        # Fitted curve
        x_dense = np.linspace(x.min(), x.max(), 300)
        y_dense = a * np.exp(b * x_dense)

    # Interpolated curve
    plt.plot(x_dense, y_dense, label=f"Regression curve")

    plt.xlabel("Number of features", fontsize=18)
    plt.ylabel(label, fontsize=18)

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)

    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    sys.modules['AlternativePaths'] = AlternativePaths
    sys.modules['SystemData'] = utils.SystemData
    sys.modules['TestSuite'] = utils.TestSuite
    #sys.modules['ErrorIsolation_Data'] = ErrorIsolation

    #initialisation_isolation_metrics(max_iterations=1)
    overall_isolation_metrics(1)
    MAM_group_metrics()

