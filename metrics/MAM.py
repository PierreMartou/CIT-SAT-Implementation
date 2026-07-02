import sys

from ErrorIsolation.ErrorIsolation import ErrorIsolationStatistics
from TestOracle.AlternativePaths import computeAlts
from metrics.OracleMetrics import printOriginalVsAlterativePaths
from utils.TestSuite import *
from ErrorIsolation import ErrorIsolation
from ErrorIsolation.ErrorIsolation import getErrorIsolation
from TestOracle.AlternativePaths import computeAlts, retrieveAlts
from TestOracle import AlternativePaths

"""
The full test suite and its alternative execution paths presented in Section 3, Table 1, are stored in 
"../data/MedicalAppointmentManager/TestSuitesCTT/runningexample.pkl"
and
"../data/MedicalAppointmentManager/AlternativePaths/runningexample-alts.pkl".

Since these files are pickled files, the following code retrieves them and un-pickles them for replication.
"""
def printRunningExampleTestSuite():
    # models = "../data/RIS-FOP/"
    models = "../data/MedicalAppointmentManager/"
    s = SystemData(featuresFile=models + 'features.txt')
    storage = models + "TestSuitesCTT/runningexample"
    altsStorage = models + "AlternativePaths/runningexample-alts"
    iteration = 1
    testsuite = computeCTTSuite(storage, s, iteration, recompute=False, verbose=True)
    # testsuite.printLatexTransitionForm()
    paths, undetectables = computeAlts(altsStorage, s, testsuite.getUnorderedTestSuite(), iteration, states=6,
                                       recompute=False)
    printOriginalVsAlterativePaths(testsuite, paths)

    lengthAndCost = [t.getShortenedLengthAndCost() for p in paths for t in p]
    averageNumberOfPaths = sum([len(p) for p in paths]) / len(paths)
    totalStates = sum([t[0] - 2 for t in lengthAndCost])
    averageLength = totalStates / len(lengthAndCost)
    totalCost = sum([t[1] for t in lengthAndCost])
    averageCost = totalCost / len(lengthAndCost)
    print("number of groups of paths is", len(paths), ", average number of paths is", averageNumberOfPaths,
          "their length is on average ", averageLength, "their cost is on average", averageCost)
    print("total number of states is", totalStates, "total cost is", totalCost)


def MAM_group_metrics(max_iterations=10):

    models = "../data/MedicalAppointmentManager/"
    s = SystemData(featuresFile=models + 'features.txt')
    storage = models + "TestSuitesCTT/"
    altsStorage = models + "AlternativePaths/alts"
    normal_storageErrorIsolation = models + "ErrorIsolation/normal/"
    random_storageErrorIsolation = models + "ErrorIsolation/random/"
    optimised_storageErrorIsolation = models + 'ErrorIsolation/optimised/o'

    group_metrics(s, storage, altsStorage, normal_storageErrorIsolation, random_storageErrorIsolation, optimised_storageErrorIsolation, max_iterations, overall=True)

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
        print(key, ' group(s) : ', random_statistics[key])
        #print(key, " : ", random_statistics[key].steps, " steps / ", random_statistics[key].SMTcalls, " SMT calls")

    all_steps = {key: random_statistics[key].steps for key in random_statistics}

    print("group initialisation : ", normal_statistics)
    if not skip_optimised:
        print("optimised : ", optimised_statistics)

    #r2_score(all_steps, degree=2)
    #r2_score(all_steps, degree=1)

    #plot_dict_with_regression(all_steps, "Average number of steps", degree=1)

def computation_time_with_N(first_N=4, second_N=20, max_iterations=10):
    models = "../data/MedicalAppointmentManager/"
    s = SystemData(featuresFile=models + 'features.txt')
    cttstorage = models + "TestSuitesCTT/"
    altsstorage = models + "AlternativePaths/alts"
    Nstorage = models + "ErrorIsolation/N/"

    max_N = 11

    time1 = 0
    time2 = 0

    N_statistics = {i: ErrorIsolationStatistics() for i in range(0, max_N)}
    N_statistics = {first_N: ErrorIsolationStatistics(), second_N: ErrorIsolationStatistics()}
    max_repetitions = 10
    #step_number = 2
    print("Computing model MAM, iteration: 0", flush=True, end='')

    for iteration in range(max_iterations):
        print("\rComputing model MAM, iteration: ", iteration, "/", max_iterations, flush=True, end='')

        for i in [first_N, second_N]:#range(0, max_N):

            error_isolation = getErrorIsolation(Nstorage+str(i)+"N_", s, cttstorage, altsstorage, iteration, states=i, recompute=True)

            for repetition in range(max_repetitions):
                #new_statistics = error_isolation.get_overall_statistics(nb_errors=1, iteration=repetition, states=i, recompute=False)
                start = time.perf_counter()
                new_statistics = error_isolation.get_statistics(3, 1, i-2)
                elapsed = time.perf_counter() - start
                if i == first_N:
                    time1 += elapsed
                else:
                    time2 += elapsed
                N_statistics[i] += new_statistics

    time1 /= (max_iterations*max_repetitions)
    time2 /= (max_iterations*max_repetitions)
    print("")
    print("Time taken with N=", first_N, ": ", time1)
    print("Time taken with N=", second_N, ": ", time2)
    for key in N_statistics:
        N_statistics[key].normalise(max_iterations*max_repetitions)
        print(key, ' : ', N_statistics[key])
        #print(key, " : ", random_statistics[key].steps, " steps / ", random_statistics[key].SMTcalls, " SMT calls")

    all_steps = {key: N_statistics[key].steps for key in N_statistics}

    print(all_steps)

if __name__ == '__main__':
    sys.modules['AlternativePaths'] = AlternativePaths
    sys.modules['SystemData'] = SystemData
    sys.modules['TestSuite'] = TestSuite
    sys.modules['ErrorIsolation'] = ErrorIsolation

    # show full test suite from Table 1
    # printRunningExampleTestSuite()

    # compares all metrics without group initialisation (1 group) / with group initialisation
    MAM_group_metrics(10)

    # compares generation time when using two different values for the hyperparameter N
    computation_time_with_N(12, 16)