import math
import pickle
from TestOracle.AlternativePaths import computeAlts
from utils.SATSolver import SATSolver
from utils.TestSuite import TestSuite, storeSuite, computeCTTSuite
from utils.TestSuite import SystemData
from CTT.CTT_heuristics import BuildingCTT
import os
import random
from TestOracle.OracleSolver import OracleSolver

def getErrorIsolation(fpath, s, storageCTT, storageAlts, iteration=0, states=10, recompute=False, recomputeSuites=False, group_mode = None, verbose=False):
    version = "1.0.0"
    file_path = fpath + "-" + str(iteration) + ".pkl"

    if os.path.exists(file_path) and not recompute:
        error_isolation = readErrorIsolation(file_path)
        #print(error_isolation.get_current_statistics())
        #print("File:", file_path, "; Statistics size:", len(error_isolation.statistics)) #, ", entries:", error_isolation.statistics.keys())
        if not error_isolation.isUpToDate(version):
            #print("Error isolation not up to date, regenerating, for file: ", fpath)
            if not isinstance(s, SystemData):
                s = SystemData(featuresFile=s)

            original_suite = computeCTTSuite(storageCTT, s, iteration, recompute=recomputeSuites, verbose=verbose)

            paths, undetectable = computeAlts(storageAlts, s, original_suite.getUnorderedTestSuite(), iteration=iteration, recompute=recomputeSuites, verbose=verbose)

            error_isolation = ErrorIsolation(file_path, s, original_suite, paths, states, version, group_mode=group_mode, verbose=verbose)
    else:
        #print("Recomputing paths for file: ", fpath)

        original_suite = computeCTTSuite(storageCTT, s, iteration=iteration, recompute=recomputeSuites, verbose=verbose)

        paths, undetectable = computeAlts(storageAlts, s, original_suite.getUnorderedTestSuite(), iteration=iteration, recompute=recomputeSuites, verbose=verbose)

        error_isolation = ErrorIsolation(file_path, s, original_suite, paths, states, version, group_mode=group_mode, verbose=verbose)

    return error_isolation

def readErrorIsolation(file_path):
    alts = pickle.load(open(file_path, 'rb'))
    return alts

def storeErrorIsolation(error_isolation, file_path):
    f = open(file_path, "wb")
    pickle.dump(error_isolation, f)
    f.close()


class ErrorIsolation:
    def __init__(self, file_path, systemData, original_suite, paths, states=4, version="1.0.0", group_mode=None, verbose=False):
        self.file_path = file_path
        self.verbose = verbose
        self.s = systemData
        self.states = states
        self.version = version
        self.original_suite = original_suite
        self.paths = paths

        self.suspects = {}
        self.groups = {}

        self.culprits = {}
        self.alts = {}

        self.statistics = {}

        self.statistics_overall = {}
        self.group_mode = group_mode

    def isUpToDate(self, version):
        return self.version == version

    def get_current_statistics(self):
        return self.statistics

    @staticmethod
    def all_combinations(activations, deactivations):
        combinations = []
        activatedFeatures = [(f, 1) for f in activations]
        deactivatedFeatures = [(f, -1) for f in deactivations]
        transitions = activatedFeatures + deactivatedFeatures
        for i in range(len(transitions)):
            for j in range(i + 1, len(transitions)):
                # ordering
                if transitions[i][0] < transitions[j][0]:
                    combinations.append((transitions[i], transitions[j]))
                else:
                    combinations.append((transitions[j], transitions[i]))
        return combinations

    @staticmethod
    def transition_is_possible(transition, initialState):
        if (initialState[transition[0][0]] > 0 and transition[0][1] > 0) or (
                initialState[transition[0][0]] < 0 and transition[0][1] < 0):
            return False
        if (initialState[transition[1][0]] > 0 and transition[1][1] > 0) or (
                initialState[transition[1][0]] < 0 and transition[1][1] < 0):
            return False
        return True

    def get_groups(self, step):
        if step in self.groups and self.groups[step] is not None:
            return self.groups[step]

        if not hasattr(self, "group_mode"):
            self.group_mode = None

        suspects = self.get_suspects(step).copy() if self.get_suspects(step) is not None else None

        if suspects is None:
            return None

        if self.group_mode is None:
            # initialising groups of suspects
            groups = []

            while suspects:
                t = BuildingCTT(self.s, verbose=False, limit=0, numCandidates=1, specificTransitionCoverage=suspects)
                testSuite = TestSuite(self.s, t.getCoveringArray(), limit=0)
                config = testSuite.getUnorderedTestSuite()[0]
                group = [s for s in suspects if self.transition_is_possible(s, config)]
                suspects = [s for s in suspects if s not in group]
                groups.append(group)

            self.groups[step] = groups
        elif self.group_mode == 1:
            self.groups[step] = [suspects]
        else:
            suspects = suspects.copy()
            random.shuffle(suspects)
            #nb_groups = math.ceil(len(self.s.getFeatures()) / 10)
            nb_groups = self.group_mode

            self.groups[step] = [
                suspects[i::nb_groups]
                for i in range(nb_groups)
                if suspects[i::nb_groups]
            ]

        self.save()
        return self.groups[step]

    def generate_paths(self, step, culprits, all_suspects):
        number_of_divides = 0
        number_of_fails = 0
        number_of_clears = 0
        number_of_change = 0
        number_of_steps = 0
        number_of_SMTcalls = 0
        step_number = step

        uncoverableTransitions = []

        groups = self.get_groups(step).copy()

        number_of_groups = len(groups)
        z3solver = OracleSolver(self.s, self.states, timeout=10000)

        startupConfig = None  # {f: -1 for f in self.s.getFeatures()}
        unsolvable_waiting_list = []
        next_groups = []
        groups.sort(key=len)
        while groups or unsolvable_waiting_list or next_groups:
            if len(groups) == 0:
                groups = next_groups
                next_groups = []
                groups.sort(key=len)

            if len(groups) == 0:
                groups = unsolvable_waiting_list
                unsolvable_waiting_list = []
                groups.sort(key=len)

            transitions_under_test = groups.pop()

            # First path, including suspects under test, excluding all other suspects.
            test_execution = z3solver.createPath(None, None,
                                                 forbiddenTransitions=[s for s in all_suspects if
                                                                       s not in transitions_under_test],
                                                 mandatoryTransitions=transitions_under_test,
                                                 startupConfig=startupConfig)
            number_of_SMTcalls += 1
            # Second path if the first didn't fail.
            if test_execution is not None:
                init_config = None  # test_execution.getUnorderedTestSuite()[0]
                alt_test_execution = z3solver.createPath(init_config, test_execution.getUnorderedTestSuite()[-1],
                                                         forbiddenTransitions=all_suspects)
                number_of_SMTcalls += 1
            else:
                alt_test_execution = None

            if test_execution is None or alt_test_execution is None:
                # no path found, we'll try with smaller groups of transitions under test.
                number_of_fails += 1

                if len(transitions_under_test) == 1:
                    uncoverableTransitions.append(transitions_under_test[0])
                else:
                    unsolvable_waiting_list.append(transitions_under_test[:round(len(transitions_under_test) / 2)])
                    unsolvable_waiting_list.append(transitions_under_test[round(len(transitions_under_test) / 2):])
            else:
                length1, cost1 = test_execution.getShortenedLengthAndCost()
                length2, cost2 = alt_test_execution.getShortenedLengthAndCost()
                number_of_change += cost1 + cost2
                number_of_steps += length1 + length2

                cleared = True

                for culprit in culprits:
                    if culprit in transitions_under_test:
                        cleared = False

                if not cleared:
                    if len(transitions_under_test) > 1:
                        number_of_divides += 1
                        next_groups.append(transitions_under_test[:round(len(transitions_under_test) / 2)])
                        next_groups.append(transitions_under_test[round(len(transitions_under_test) / 2):])
                else:
                    number_of_clears += 1
        return ErrorIsolationStatistics(number_of_divides, number_of_fails, number_of_clears, number_of_change, number_of_steps, number_of_SMTcalls, number_of_groups, step_number)

    def isolate_errors(self, step, nb_errors, states, verbose=True):
        all_suspects = self.get_suspects(step).copy()
        combination = (step, nb_errors, states)

        if len(all_suspects) == 0:
            self.statistics[combination] = ErrorIsolationStatistics(0, 0, 0, 0, 0)
            return

        culprits = random.sample(all_suspects, nb_errors)
        self.culprits[combination] = culprits
        statistics = self.generate_paths(step, culprits, all_suspects)

        self.statistics[combination] = statistics

    def get_suspects(self, step):
        if step in self.suspects and self.suspects[step] is not None:
            return self.suspects[step]

        suspects = []

        original_next = self.original_suite.getUnorderedTestSuite()[step]

        if step == 0:
            prev = {f: -1 for f in self.original_suite.getUnorderedTestSuite()[0]}
            activations = [f for f in prev if prev[f] < 0 and original_next[f] > 0]
            deactivations = [f for f in prev if prev[f] > 0 and original_next[f] < 0]
            suspects = self.all_combinations(activations, deactivations)
        else:
            prev = self.original_suite.getUnorderedTestSuite()[step - 1]

            activations = [f for f in prev if prev[f] < 0 and original_next[f] > 0]
            deactivations = [f for f in prev if prev[f] > 0 and original_next[f] < 0]
            suspects = self.all_combinations(activations, deactivations)

            alt_paths = self.paths[step - 1]

            if len(alt_paths) > 0:
                alt_path = random.choice(alt_paths)

                for alt_next in alt_path.getUnorderedTestSuite():
                    activations = [f for f in prev if prev[f] < 0 and alt_next[f] > 0]
                    deactivations = [f for f in prev if prev[f] > 0 and alt_next[f] < 0]

                    allcombi = self.all_combinations(activations, deactivations)
                    filtering = [combi for combi in allcombi if combi not in suspects]
                    suspects = suspects + filtering

                    prev = alt_next

                activations = [f for f in prev if prev[f] < 0 and original_next[f] > 0]
                deactivations = [f for f in prev if prev[f] > 0 and original_next[f] < 0]

                allcombi = self.all_combinations(activations, deactivations)
                filtering = [combi for combi in allcombi if combi not in suspects]
                suspects = suspects + filtering

        if step > 1:
            previously_cleared_transitions = self.get_overall_suspects([self.get_suspects(i) for i in range(1, step)])
            suspects = [s for s in suspects if s not in previously_cleared_transitions]

        # preprocessing undecomposable transitions from suspects.
        # print(suspects)
        satSolver = SATSolver(self.s)
        decomposables = []
        nonDecomposables = []
        for t in suspects:
            # indexedT = [self.s.toIndex(f[1:]) if f[0:1] == '+' else -self.s.toIndex(f[1:]) for f in t]
            if self.decomposableTransition(satSolver, t):
                decomposables.append(t)
            else:
                nonDecomposables.append(t)

        self.suspects[step] = decomposables.copy()

        self.save()

        return self.suspects[step]

    def decomposableTransition(self, solver, transition):
        values = []
        for i in range(len(transition)):
            for j in range(len(transition)):
                f = transition[j]
                values.append(f[1] if i != j else -1 * f[1])
            if solver.checkSAT(values):
                return True
        return False

    def get_all_suspects(self):
        all_suspects = []
        for i in range(1, len(self.original_suite.getUnorderedTestSuite())):
            all_suspects.append(self.get_suspects(i))
        return all_suspects

    def get_statistics(self, step, nb_errors, nb_state):
        combination = (step, nb_errors, nb_state)
        if combination not in self.statistics or self.statistics[combination] is None:
            self.isolate_errors(step, nb_errors, nb_state)
            self.save()

        return self.statistics[combination]

    def get_all_statistics(self, nb_errors, states=None):
        if states is None:
            states = [10]
        toReturn = {}
        for i in range(1, len(self.original_suite.getUnorderedTestSuite())):
            for nb_error in nb_errors:
                for state in states:
                    combination = (i, nb_error, state)
                    toReturn[combination] = self.get_statistics(i, nb_error, state)

        return toReturn

    def get_overall_statistics(self, nb_errors=1, iteration=0, states=10, recompute=False):
        combination = (nb_errors, iteration, states)

        if not hasattr(self, 'statistics_overall'):
            self.statistics_overall = {}

        if recompute or combination not in self.statistics_overall:
            all_suspects = self.get_all_suspects()
            overall_suspects = self.get_overall_suspects(all_suspects)

            current_suspects = []
            original_culprit = None
            step = 0
            stopgap = 10
            stop = 0

            while len(current_suspects) < nb_errors and stop < stopgap:
                original_culprit = random.sample(overall_suspects, 1)[0]
                step = self.find_step(original_culprit)
                current_suspects = all_suspects[step-1]
                stop += 1
                if step > 1:
                    previously_cleared_transitions = self.get_overall_suspects(all_suspects[:step-1])
                    current_suspects = [s for s in current_suspects if s not in previously_cleared_transitions]

            # there is no path where the number of suspects is higher than the number of errors, so it's impossible to compute.
            if stop == stopgap:
                self.statistics_overall[combination] = None
            else:


                culprits = [original_culprit]

                while len(culprits) < nb_errors:
                    new_culprit = random.sample(current_suspects, 1)
                    if new_culprit not in culprits:
                        culprits.append(new_culprit)

                curr_statistics = self.generate_paths(step, culprits, current_suspects)
                self.statistics_overall[combination] = curr_statistics

            self.save()

        return self.statistics_overall[combination]

    def find_step(self, culprit):
        all_suspects = self.get_all_suspects()
        for i in range(len(all_suspects)):
            analysing = all_suspects[i]
            if culprit in analysing:
                return i+1

    def get_overall_suspects(self, lists):
        seen = set()
        result = []
        for lst in lists:
            for x in lst:
                if x not in seen:
                    seen.add(x)
                    result.append(x)
                else:
                    print("there still duplication")
        return result

    def statistics_exist(self, nb_errors, states=None):
        if states is None:
            states = [10]
        for i in range(1, len(self.original_suite.getUnorderedTestSuite())):
            for nb_error in nb_errors:
                for state in states:
                    combination = (i, nb_error, state)
                    if combination not in self.statistics:
                        return False
        return True

    def save(self):
        f = open(self.file_path, "wb")
        pickle.dump(self, f)
        f.close()


class ErrorIsolationStatistics:
    def __init__(self, divides=0, fails=0, clears=0, changes=0, steps=0, SMTcalls=0, number_of_groups=0, step_number = 1):
        self.divides = self.average_list(divides)
        self.fails = self.average_list(fails)
        self.clears = self.average_list(clears)
        self.changes = self.average_list(changes)
        self.steps = self.average_list(steps)
        self.SMTcalls = self.average_list(SMTcalls)
        self.number_of_groups = self.average_list(number_of_groups)
        self.step_number = self.average_list(step_number)

    def __add__(self, other):
        if not isinstance(other, ErrorIsolationStatistics):
            return NotImplemented

        return ErrorIsolationStatistics(
            self.divides + other.divides,
            self.fails + other.fails,
            self.clears + other.clears,
            self.changes + other.changes,
            self.steps + other.steps,
            self.SMTcalls + other.SMTcalls,
            self.number_of_groups + other.number_of_groups,
            self.step_number + self.step_number,
        )

    def __str__(self):
        return (
            f"ErrorIsolationStatistics("
            f"divides={self.divides}, "
            f"fails={self.fails}, "
            f"clears={self.clears}, "
            f"changes={self.changes}, "
            f"changes={self.steps}, "
            f"changes={self.SMTcalls}, "
            f"changes={self.number_of_groups}, "
            f"steps={self.step_number}"
            f")"
        )

    def normalise(self, iterations):
        self.divides /= iterations
        self.fails /= iterations
        self.clears /= iterations
        self.changes /= iterations
        self.steps /= iterations
        self.SMTcalls /= iterations
        self.number_of_groups /= iterations
        self.step_number /= iterations

    @staticmethod
    def average_list(l):
        if type(l) is list:
            return sum(l)/len(l)
        else:
            return l

    """"@staticmethod
    def aggregate_steps(statistics):
        avg_step = 0
        for (step, nb_errors, state) in statistics:
            if step in aggregated_statistics:
                aggregated_statistics[step].append(statistics(step, nb_errors, state))
            else:
                aggregated_statistics[step] ="""

