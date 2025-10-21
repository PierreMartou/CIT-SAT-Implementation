from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner
from TestOracle.OracleSolver import OracleSolver
from utils.SATSolver import SATSolver
from utils.TestSuite import computeCTTSuite
from CTT.CTT_heuristics import BuildingCTT
from utils.TestSuite import TestSuite, storeSuite
from utils.TestSuite import SystemData
import os


# TODO WARNING DOES NOT FIND ACCURATE SUSPECTS FOR ALTERNATIVE PATH
def find_suspects(original_path, alt_path, step):
    suspects = []
    for path in [original_path, alt_path]:
        [activations, deactivations] = TestingToolRunner.activations_at_specific_step(step, path)
        activatedFeatures = {f:1 for f in activations}
        deactivatedFeatures = {f:-1 for f in deactivations}
        print("currently not working with alternative path")
        for i in range(len(activatedFeatures) + len(deactivatedFeatures)):
            for j in range(i+1, len(features)):
                # ordering
                if features[i][1:] < features[j][1:]:
                    suspects.append((features[i], features[j]))
                else:
                    suspects.append((features[j], features[i]))

    return suspects

def error_isolation(controller, testing_tool_folder, feature_model_path, alt_number, reference, step, states=4):

    system_data = SystemData(featuresFile=feature_model_path)

    #will be used to find initial states
    satsolver = SATSolver(system_data)

    #will be used to find alternative paths
    z3solver = OracleSolver(system_data, states)

    # step 1 : find suspects
    original_path = testing_tool_folder + "paths" + str(reference) + '-' + '0.txt'
    alt_path = testing_tool_folder + "paths" + str(reference) + '-' + str(alt_number) + '.txt'

    suspects = find_suspects(original_path, alt_path, step)
    all_suspects = suspects.copy()
    culprits = []
    # step 2 : create biggest (hopefully valid but not sure) groups. Aim for biggest, then biggest with the rest until all suspects are in a group. Can use CTT principles for that ?
    groups = []
    while suspects:
        t = BuildingCTT(system_data, verbose=False, limit=0, specificTransitionCoverage=suspects)
        testSuite = TestSuite(system_data, t.getCoveringArray(), limit=0)
        config = testSuite.getUnorderedTestSuite()[0]
        group = [s for s in suspects if transitionIsPossible(s, config)]
        suspects = [s for s in suspects if s not in group]
        groups.append(group)

    print("final groups, ", len(groups))

    # step 3 : reuse alternative paths algorithms to create alt paths, dichotomic search, but forbid all transitions still in the suspects.
    uncoverableTransitions = []
    startupConfig = {f:-1 for f in system_data.getFeatures()}
    unsolvable_waiting_list = []
    while groups:
        transitions_under_test = groups.pop()
        # create alternate path for group

        # maybe create a single z3 execution
        test_execution = z3solver.createPath(None, None, [s for s in all_suspects if s not in transitions_under_test], mandatoryTransitions=transitions_under_test, startupConfig=startupConfig)
        print(test_execution)
        # no need for a start up config if the initial path already takes it into account
        if test_execution is not None:
            alt_test_execution = z3solver.createPath(test_execution.getUnorderedTestSuite()[0], test_execution.getUnorderedTestSuite()[-1], all_suspects)
        else:
            alt_test_execution = None

        if test_execution is None or alt_test_execution is None:
            # no path found, we'll try with smaller groups of transitions under test.
            if len(transitions_under_test) > 1:
                groups.append(transitions_under_test[:round(len(transitions_under_test)/2)])
                groups.append(transitions_under_test[round(len(transitions_under_test)/2):])
            else:
                uncoverableTransitions.append(transitions_under_test[0])
        else:
            # reuse test oracle executioner to assess if they are innocent

            # TODO store the two paths in testing tool folder as 0-0 and 1-0
            storeSuite(test_execution, os.path.join(testing_tool_folder, f"paths{reference}-0.txt"))

            storeSuite(alt_test_execution, os.path.join(testing_tool_folder, f"paths{reference}-1.txt"))

            discrepancies = TestingToolRunner.launch_test_oracle(controller, testing_tool_folder, feature_model_path, skip_generation=True, reference=reference+1, verbose=False)

            if not discrepancies:
                # all innocent
                all_suspects = [s for s in all_suspects if s not in transitions_under_test]
            else:
                if len(transitions_under_test) > 1:
                    # adding smaller groups to locate the culprit
                    groups.append(transitions_under_test[:round(len(transitions_under_test)/2)])
                    groups.append(transitions_under_test[round(len(transitions_under_test)/2):])
                else:
                    # culprit found. it has to stay in suspects, but the group is done.
                    culprits.append(transitions_under_test[0])
    return culprits, uncoverableTransitions

def transitionIsPossible(transition, initialState):
    if (initialState[transition[0][1:]] > 0 and transition[0][:1] == '+') or (initialState[transition[0][1:]] < 0 and transition[0][:1] == '-'):
        return False
    if (initialState[transition[1][1:]] > 0 and transition[1][:1] == '+') or (initialState[transition[1][1:]] < 0 and transition[1][:1] == '-'):
        return False
    return True



