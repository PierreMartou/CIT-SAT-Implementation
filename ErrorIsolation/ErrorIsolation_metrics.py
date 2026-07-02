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



def average_de_activations(max_iterations=5):
    modelFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txt/"
    constraintsFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txtconstraints/"
    storageCTT = "../data/SPLOT/SPLOT-NEW/SPLOT-TestSuitesCTT/"
    storageAlts = "../data/SPLOT/SPLOT-NEW/SPLOT-Alts/"
    storageErrorIsolation = "../data/SPLOT/SPLOT-NEW/SPLOT-ErrorIsolation/default/"

    nb_groups = {}

    average_ctt_size = {}
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

        verbose = False
        curr_nb_groups = 0
        curr_avg_suspects = 0
        curr_avg_cost = 0
        curr_steps = 0

        curr_ctt_size = 0


        error_isolation = getErrorIsolation(tempStorageErrorIsolation, s, tempStorageCTT, tempstorageAlts, verbose=verbose)

        all_suspects = error_isolation.get_all_suspects()
        curr_avg_suspects += sum([len(s) for s in all_suspects]) / len(all_suspects)

        for iteration in range(max_iterations):
            print("\rComputing model " + str(quty) + "/" + str(total), iteration + 1, "/", max_iterations,
                  " (category: " + str("all, size: ") + str(len(s.getFeatures())) + "), model " + str(filename), flush=True, end='')

            if verbose:
                print("")

            computedSuite = computeCTTSuite(tempStorageCTT, s, iteration=iteration)
            curr_avg_cost += computedSuite.getCost()/computedSuite.getLength()

            paths, undetectable = computeAlts(tempstorageAlts, s, computedSuite.getUnorderedTestSuite(), iteration=iteration)
            alts_cost = []
            for p in paths:
                if len(p) > 0:
                   alts_cost.append(sum(t.getCost() for t in p)/len(p))

            curr_avg_cost += sum(alts_cost)/len(alts_cost)

            groups = error_isolation.get_groups(1)

            #all_stats = error_isolation.get_all_statistics(nb_errors=[1], states=[10])
            #all_steps = [error_isolation.get_statistics(1, 1, 10)]
            #all_steps = []
            #for key in all_stats:
            #    all_steps.append(all_stats[key].steps)
            #curr_steps += sum(all_steps)/len(all_steps)

            if groups is not None:
                curr_nb_groups += len(groups)


        #curr_statistics

        average_cost.setdefault(nb_features, []).append(curr_avg_cost / max_iterations)
        average_suspects.setdefault(nb_features, []).append(curr_avg_suspects)
        average_steps.setdefault(nb_features, []).append(curr_steps / max_iterations)

        # print(average_steps)

        result = curr_nb_groups/max_iterations
        if nb_features in nb_groups:
            nb_groups[nb_features] = nb_groups[nb_features] + [result]
        else:
            nb_groups[nb_features] = [result]

    #average_suspects.setdefault(91, []).append(60)
    average_suspects = aggregate_data(average_suspects, step=10)
    r2_score(average_suspects)
    r2_score(average_suspects, degree=1)
    plot_dict_with_regression(average_suspects, "Average number of suspects", degree=2)

    #average_suspects = aggregate_data(average_suspects)
    #plot_dict_with_regression(average_suspects, "Average number of suspects", degree=1)

def overall_isolation_metrics(max_iterations = 10, group_mode = None):
    modelFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txt/"
    constraintsFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txtconstraints/"
    storageCTT = "../data/SPLOT/SPLOT-NEW/SPLOT-TestSuitesCTT/"
    storageAlts = "../data/SPLOT/SPLOT-NEW/SPLOT-Alts/"
    if group_mode is None:
        storageErrorIsolation = "../data/SPLOT/SPLOT-NEW/SPLOT-ErrorIsolation/default/"
    else:
        storageErrorIsolation = "../data/SPLOT/SPLOT-NEW/SPLOT-ErrorIsolation/"+str(group_mode)+"groups/"

    all_statistics = {}
    only_if_exists = False
    comparisons = {}
    betternormal = {}
    storage_error_isolation_1group = "../data/SPLOT/SPLOT-NEW/SPLOT-ErrorIsolation/1groups/"

    #nb_errors = [1, 2, 3]

    quty = 0
    stopping = 500
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

        #if group_mode is not None:
        #    if nb_features < 60 and nb_features in all_statistics:
        #       continue
        tempStorageCTT = storageCTT + filename[:-4] + "-1&2&3-"
        tempstorageAlts = storageAlts + filename[:-4]
        tempStorageErrorIsolation = storageErrorIsolation + filename[:-4]

        verbose = False
        curr_statistics = ErrorIsolationStatistics()
        curr_compared_statistics = ErrorIsolationStatistics()

        error_isolation = getErrorIsolation(tempStorageErrorIsolation, s, tempStorageCTT, tempstorageAlts,
                                            verbose=verbose, group_mode=group_mode)

        #error_isolation_comparison = getErrorIsolation(storage_error_isolation_1group, s, tempStorageCTT, tempstorageAlts, verbose=verbose, group_mode=1)

        for iteration in range(max_iterations):
            print("\rComputing model " + str(quty) + "/" + str(total), iteration + 1, "/", max_iterations,
                  " (category: " + str("all, size: ") + str(len(s.getFeatures())) + "), model " + str(filename),
                  flush=True, end='')

            new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=iteration, states=10, recompute=False, only_if_exists=only_if_exists)
            #new_statistics = error_isolation.get_statistics(1, 1, 1)

            #compared_statistics = error_isolation_comparison.get_overall_statistics(nb_errors=1, iteration=iteration, states=10, recompute=False)

            #curr_compared_statistics = curr_compared_statistics + compared_statistics

            #if new_statistics.divides == 0:
            #    print("here: ", filename)
            if new_statistics is not None:
                curr_statistics = curr_statistics + new_statistics

        # curr_statistics
        curr_statistics.normalise(max_iterations)
        #curr_compared_statistics.normalise(max_iterations)

        #comparisons[nb_features] = comparisons.setdefault(nb_features, 0) + 1
        #if curr_compared_statistics.steps > curr_statistics.steps:
        #    betternormal.setdefault(nb_features, []).append(1)
        #else:
        #    betternormal.setdefault(nb_features, []).append(0)

        all_statistics.setdefault(nb_features, []).append(curr_statistics)

    # plot_dict_with_regression(average_cost, "Average number of (de)activations", degree=1)

    #return betternormal

    # do something with comparison and betternormal

    return all_statistics


def MAM_group_metrics(max_iterations=10):

    models = "../data/MedicalAppointmentManager/"
    s = SystemData(featuresFile=models + 'features.txt')
    storage = models + "TestSuitesCTT/"
    altsStorage = models + "AlternativePaths/alts"
    normal_storageErrorIsolation = models + "ErrorIsolation/normal/"
    random_storageErrorIsolation = models + "ErrorIsolation/random/"
    optimised_storageErrorIsolation = models + 'ErrorIsolation/optimised/o'

    group_metrics(s, storage, altsStorage, normal_storageErrorIsolation, random_storageErrorIsolation, optimised_storageErrorIsolation, max_iterations, overall=True)


def MAM_N_metrics(max_iterations=10):
    models = "../data/MedicalAppointmentManager/"
    s = SystemData(featuresFile=models + 'features.txt')
    storage = models + "TestSuitesCTT/"
    altsStorage = models + "AlternativePaths/alts"
    N_storageErrorIsolation = models + "ErrorIsolation/N/"

    N_metrics(s, storage, altsStorage, N_storageErrorIsolation, max_iterations)

def SPLOTsingleModel(max_iterations = 3):
    filename = "model_20120725_1460954667.txt"
    modelFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txt/"
    constraintsFiles = "../data/SPLOT/SPLOT-NEW/SPLOT-txtconstraints/"
    filename = 'model_20140424_1672030888.txt'

    txt = os.path.join(modelFiles, filename)
    txtConstraints = os.path.join(constraintsFiles, filename)
    s = SystemData(featuresFile=txt, extraConstraints=txtConstraints)

    base = "../data/SPLOT/HandpickedModels/"
    storage = base + "ctt"
    altsStorage = base + "alts"
    normal_storageErrorIsolation = base + "normal"
    random_storageErrorIsolation = base + "random"
    optimised_storageErrorIsolation = base + "optimised"

    group_metrics(s, storage, altsStorage, normal_storageErrorIsolation, random_storageErrorIsolation, optimised_storageErrorIsolation, max_iterations)

def group_metrics(s, cttstorage, altsstorage, normalstorage, randomstorage, optimisedstorage, max_iterations=10, overall=False):
    normal_statistics = ErrorIsolationStatistics()
    optimised_statistics = ErrorIsolationStatistics()
    max_repetitions = 10
    max_groups = 2
    random_statistics = {i: ErrorIsolationStatistics() for i in range(1, max_groups)}
    step_number = 2
    skip_optimised = True

    print("Computing model MAM, iteration: 0", flush=True, end='')

    for iteration in range(max_iterations):
        print("\rComputing model MAM, iteration: ", iteration, "/", max_iterations, flush=True, end='')

        error_isolation = getErrorIsolation(normalstorage, s, cttstorage, altsstorage, iteration,
                                            group_mode=None)

        if not skip_optimised:
            optimised_error_isolation = getErrorIsolation(optimisedstorage, s, cttstorage, altsstorage, iteration,
                                            group_mode=-2)

        for repetition in range(max_repetitions):
            if overall:
                new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=10, recompute=False)
            else:
                new_statistics = error_isolation.get_statistics(step_number, 1, 10)
            normal_statistics += new_statistics

            if not skip_optimised:
                if overall:
                    new_statistics = optimised_error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=10, recompute=False)
                else:
                    new_statistics = optimised_error_isolation.get_statistics(step_number, 1, 10)
                optimised_statistics += new_statistics

            #print("normal, steps : ", new_statistics.step_number)
            #print("current amount of step number : ", normal_statistics.step_number)
        for i in range(1, max_groups):
            error_isolation = getErrorIsolation(randomstorage+str(i)+"groups_", s, cttstorage, altsstorage, iteration,
                                                group_mode=i)

            for repetition in range(max_repetitions):
                if overall:
                    new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=10, recompute=False)
                else:
                    new_statistics = error_isolation.get_statistics(step_number, 1, 10)
                random_statistics[i] += new_statistics

    normal_statistics.normalise(max_iterations*max_repetitions)
    if not skip_optimised:
        optimised_statistics.normalise(max_iterations*max_repetitions)
    print("")
    for key in random_statistics:
        random_statistics[key].normalise(max_iterations*max_repetitions)
        print(key, ' : ', random_statistics[key])
        #print(key, " : ", random_statistics[key].steps, " steps / ", random_statistics[key].SMTcalls, " SMT calls")

    all_steps = {key: random_statistics[key].steps for key in random_statistics}

    print("normal : ", normal_statistics)
    if not skip_optimised:
        print("optimised : ", optimised_statistics)

    #r2_score(all_steps, degree=2)
    #r2_score(all_steps, degree=1)

    #plot_dict_with_regression(all_steps, "Average number of steps", degree=1)

def N_metrics(s, cttstorage, altsstorage, Nstorage, max_iterations=10, overall=False):
    max_N = 11

    time4 = 0
    time20 = 0

    comparison = 14

    N_statistics = {i: ErrorIsolationStatistics() for i in range(0, max_N)}
    N_statistics = {4: ErrorIsolationStatistics(), comparison: ErrorIsolationStatistics()}
    max_repetitions = 10
    #step_number = 2
    print("Computing model MAM, iteration: 0", flush=True, end='')

    for iteration in range(max_iterations):
        print("\rComputing model MAM, iteration: ", iteration, "/", max_iterations, flush=True, end='')

        for i in [4, comparison]:#range(0, max_N):

            error_isolation = getErrorIsolation(Nstorage+str(i)+"N_", s, cttstorage, altsstorage, iteration, states=i, recompute=True)

            for repetition in range(max_repetitions):
                #new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=i, recompute=False)
                start = time.perf_counter()
                new_statistics = error_isolation.get_statistics(3, 1, i-2)
                elapsed = time.perf_counter() - start
                if i == 4:
                    time4 += elapsed
                else:
                    time20+= elapsed
                N_statistics[i] += new_statistics

    time4 /= (max_iterations*max_repetitions)
    time20 /= (max_iterations*max_repetitions)
    print("")
    print("Time taken with N=4: ", time4)
    print("Time taken with N=20: ", time20)
    for key in N_statistics:
        N_statistics[key].normalise(max_iterations*max_repetitions)
        print(key, ' : ', N_statistics[key])
        #print(key, " : ", random_statistics[key].steps, " steps / ", random_statistics[key].SMTcalls, " SMT calls")

    all_steps = {key: N_statistics[key].steps for key in N_statistics}

    print(all_steps)

def r2_score_helper(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - ss_res / ss_tot

def r2_score(y_true, degree=2):
    x = np.array(sorted(y_true.keys()))
    y = np.array([y_true[k] for k in x])

    coeffs = np.polyfit(x, y, deg=degree)
    poly = np.poly1d(coeffs)

    y_hat = poly(x)

    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)

    r2 = 1 - ss_res / ss_tot

    print(f"(degree {degree}) R² = {r2:.3f}")

def aggregate_data(data, min=0, max=100, step=10, key=None):
    new_average_suspects = {}
    for i in range(min, max, step):
        aggregation = []
        for j in range(i, i + step):
            if j in data:
                if key is None:
                    aggregation.extend(data[j])
                else:
                    aggregation.extend(getattr(x, key) for x in data[j])
        if len(aggregation) > 0:
            new_average_suspects[i + math.ceil(step/2)] = sum(aggregation) / len(aggregation)

    return new_average_suspects


def table_all_stats_SPLOT(max_iterations=10):
    all_statistics = overall_isolation_metrics(max_iterations, None)

    range_categories = [(10, 25), (25, 50), (50, 75), (75, 100)]

    new_statistics = {category: ErrorIsolationStatistics() for category in range_categories}

    for r in range_categories:
        r_stats = ErrorIsolationStatistics()
        quty = 0
        for key in all_statistics:
            if key > r[0] and key <= r[1]:
                if key > 70:
                    print(key)
                for a in all_statistics[key]:
                    r_stats += a
                quty += len(all_statistics[key])
        r_stats.normalise(quty)
        new_statistics[r] = r_stats
    print("")
    for r in new_statistics:
        print(r)
        print(
            f"{new_statistics[r].number_of_groups:.2f} & "
            f"{new_statistics[r].clears:.2f} & "
            f"{new_statistics[r].divides:.2f} & "
            f"{new_statistics[r].fails:.2f} & "
            f"{new_statistics[r].SMTcalls:.2f} & "
            f"{new_statistics[r].steps:.2f} & "
            f"{new_statistics[r].changes:.2f}"
        )
        #print(new_statistics[r])

def plotgroupSPLOT(max_iterations=5):
    all_statistics1group = overall_isolation_metrics(max_iterations, 1)

    all_statisticsnormal = overall_isolation_metrics(max_iterations, None)
    print(all_statistics1group)
    metric = "steps"
    #metric = None

    steps_1group = aggregate_data(all_statistics1group, step=10, key=metric)
    steps_normal = aggregate_data(all_statisticsnormal, step=10, key=metric)

    degree1group, r2certainty_1group = best_certainty(steps_1group)
    degreenormal, r2certainty_normal = best_certainty(steps_normal)

    print("\nFor normal: ", degreenormal, " degree, R2 : ", r2certainty_normal)
    print("For 1group: ", degree1group, " degree, R2 : ", r2certainty_1group)

    plot_dict_with_regression(steps_1group, "Size", degree=degree1group, scatter=False, label=f"Without group initialisation")
    plot_dict_with_regression(steps_normal, "Size", degree=degreenormal, scatter=False, label="With group initialisation")

    if metric == "SMTcalls":
        plt.ylabel("Number of SMT calls", fontsize=18)
    else:
        plt.ylabel("Size", fontsize=18)


    plt.xlabel("Number of features", fontsize=18)

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)

    plt.legend(fontsize=16)
    plt.grid(True)
    if metric is None:
        metric = "percentagebetter"
    plt.savefig(metric+".png", dpi=300, bbox_inches="tight")

    plt.show()

def best_certainty(data):
    best_degree = 0
    best_r2_score = 0

    for degree in[1, 2, "exp", "log"]:
        curr_r2 = plot_dict_with_regression(data, "", degree=degree, scatter=False, label="", needr2=True)
        print("computing with degree ", degree, "; r2: ", curr_r2)
        if curr_r2 > best_r2_score:
            best_degree = degree
            best_r2_score = curr_r2
    return best_degree, best_r2_score

def plot_dict_with_regression(d, ylabel, degree=2, scatter=True, label=f"Regression curve", needr2=False):
    # Sort by X
    x = np.array(sorted(d.keys()))
    y = np.array([d[k] for k in x])
    r2 = None
    # Scatter points
    if scatter:
        plt.scatter(x, y, label=f"Aggregated data")
    if type(degree) == int:
        coeffs = np.polyfit(x, y, deg=degree)
        poly = np.poly1d(coeffs)

        y_pred = poly(x)
        r2 = r2_score_helper(y, y_pred)

        x_dense = np.linspace(x.min(), x.max(), 300)
        y_dense = poly(x_dense)
    elif degree == "exp":
        logy = np.log(y)
        b, loga = np.polyfit(x, logy, deg=1)
        a = np.exp(loga)

        y_pred = a * np.exp(b * x)
        r2 = r2_score_helper(y, y_pred)

        # Fitted curve
        x_dense = np.linspace(x.min(), x.max(), 300)
        y_dense = a * np.exp(b * x_dense)
    elif degree == "log":
        logx = np.log(x)
        a, b = np.polyfit(logx, y, deg=1)

        y_pred = a * np.log(x) + b
        r2 = r2_score_helper(y, y_pred)

        x_dense = np.linspace(x.min(), x.max(), 300)
        y_dense = a * np.log(x_dense) + b

    if needr2:
        return r2

    # Interpolated curve
    plt.plot(x_dense, y_dense, label=label)

    if scatter:
        plt.xlabel("Number of features", fontsize=18)
        plt.ylabel(ylabel, fontsize=18)

        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)

        plt.xlabel("Number of features", fontsize=18)
        plt.legend(fontsize=16)
        plt.grid(True)
        plt.savefig(ylabel+".png", dpi=300, bbox_inches="tight")
        plt.show()

if __name__ == '__main__':
    sys.modules['AlternativePaths'] = AlternativePaths
    sys.modules['SystemData'] = utils.SystemData
    sys.modules['TestSuite'] = utils.TestSuite
    #sys.modules['ErrorIsolation_Data'] = ErrorIsolation

    # Figure 6.2
    average_de_activations(max_iterations=5)

    # Figure 6.4
    plotgroupSPLOT("steps", 3)
    plotgroupSPLOT("SMTcalls", 3)

    # Table 6.2
    table_all_stats_SPLOT(5)

    # utils
    # overall_isolation_metrics(2, group_mode=None)
    # SPLOTsingleModel(2)
