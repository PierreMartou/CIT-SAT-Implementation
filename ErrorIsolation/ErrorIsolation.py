from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner
from TestOracle.OracleSolver import OracleSolver
from utils.SATSolver import SATSolver
from utils.TestSuite import computeCTTSuite
from CTT.CTT_heuristics import BuildingCTT
from utils.TestSuite import TestSuite, storeSuite
from utils.TestSuite import SystemData
import os

def testing_z3solver(feature_model_path):
    system_data = SystemData(featuresFile=feature_model_path)

    # will be used to find initial states
    # satsolver = SATSolver(system_data)

    # will be used to find alternative paths
    z3solver = OracleSolver(system_data, 4)
    startupConfig = {f: -1 for f in system_data.getFeatures()}

    all_suspects = [(('High', -1), ('Low', 1))]
    transitions_under_test = [(('High', -1), ('Low', 1))]
    test_execution = z3solver.createPath(None, None, [s for s in all_suspects if s not in transitions_under_test],
                                         mandatoryTransitions=transitions_under_test, startupConfig=startupConfig)

    print(test_execution.printLatexTransitionForm())

def find_suspects(original_path, alt_path, step):
    suspects = []
    for path in [original_path, alt_path]:
        all_transitions = TestingToolRunner.activations_at_specific_step(step, path)
        for [activations, deactivations] in all_transitions:
            suspects.append(all_combinations(activations, deactivations))

    return suspects

# Takes two lists of features (where a feature is a String)
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

def find_suspects_SPLOT(original_suite, alternatives, step):
    suspects = []
    if step > 0:
        prev = original_suite.getUnorderedTestSuite()[step-1]
    else:
        prev = {f: -1 for f in original_suite.getUnorderedTestSuite()[0]}

    original_next = original_suite.getUnorderedTestSuite()[step]

    for next in [original_next] + alternatives[step-1]:
        activations = [f for f in prev if prev[f] < 0 and next[f] > 0]
        deactivations = [f for f in prev if prev[f] > 0 and next[f] < 0]
        suspects.append(all_combinations(activations, deactivations))

        prev = next

    return suspects

def group_initialisation(suspects, system_data):
    groups = []
    while suspects:
        t = BuildingCTT(system_data, verbose=False, limit=0, specificTransitionCoverage=suspects)
        testSuite = TestSuite(system_data, t.getCoveringArray(), limit=0)
        config = testSuite.getUnorderedTestSuite()[0]
        group = [s for s in suspects if transitionIsPossible(s, config)]
        suspects = [s for s in suspects if s not in group]
        groups.append(group)

    return groups

def error_isolation(controller, testing_tool_folder, feature_model_path, alt_number, reference, step, states=4, verbose=False):

    system_data = SystemData(featuresFile=feature_model_path)

    #will be used to find initial states
    #satsolver = SATSolver(system_data)

    #will be used to find alternative paths
    z3solver = OracleSolver(system_data, states)

    # step 1 : find suspects
    original_path = testing_tool_folder + "paths" + str(reference) + '-' + '0.txt'
    alt_path = testing_tool_folder + "paths" + str(reference) + '-' + str(alt_number) + '.txt'

    suspects = find_suspects(original_path, alt_path, step)
    #for s in suspects:
    #    if s[0][0] in ["High", "Low"]:
    #        print(s)

    all_suspects = suspects.copy()
    culprits = []
    # step 2 : create biggest (hopefully valid but not sure) groups. Aim for biggest, then biggest with the rest until all suspects are in a group. Can use CTT principles for that ?

    groups = group_initialisation(suspects, system_data)

    #print("\nFinal groups: ", len(groups))

    # step 3 : reuse alternative paths algorithms to create alt paths, dichotomic search, but forbid all transitions still in the suspects.
    uncoverableTransitions = []
    number_of_fails = 0
    number_of_divide = 0
    startupConfig = {f: -1 for f in system_data.getFeatures()}
    unsolvable_waiting_list = []
    while groups:
        transitions_under_test = groups.pop()
        testing = False
        if (('High', -1), ('Low', 1)) in transitions_under_test:
            print("testing culprit")
            testing = True
        # first path, including suspects under test
        test_execution = z3solver.createPath(None, None, [s for s in all_suspects if s not in transitions_under_test], mandatoryTransitions=transitions_under_test, startupConfig=startupConfig)

        if test_execution is not None:
            alt_test_execution = z3solver.createPath(test_execution.getUnorderedTestSuite()[0], test_execution.getUnorderedTestSuite()[-1], all_suspects)
        else:
            alt_test_execution = None

        if test_execution is None or alt_test_execution is None:
            # no path found, we'll try with smaller groups of transitions under test.
            number_of_fails += 1
            if len(transitions_under_test) > 1:
                groups.append(transitions_under_test[:round(len(transitions_under_test)/2)])
                groups.append(transitions_under_test[round(len(transitions_under_test)/2):])
            else:
                uncoverableTransitions.append(transitions_under_test[0])
        else:
            # reuse test oracle executioner to assess if they are innocent

            #storeSuite(test_execution, os.path.join(testing_tool_folder, f"paths{reference+}-0.txt"))
            #storeSuite(alt_test_execution, os.path.join(testing_tool_folder, f"paths{reference+1}-1.txt"))
            for i in range(2):
                try:
                    filePath = os.path.join(testing_tool_folder, f"paths{reference+1}-{i}.txt")
                    file = open(filePath, "w")
                    file.write(str(2) + "\n")
                    file.write(str(0) + "% undetectables")
                    if i == 0:
                        completeSuite = [startupConfig] + test_execution.getUnorderedTestSuite()
                    else:
                        completeSuite = [startupConfig] + alt_test_execution.getUnorderedTestSuite()

                    for j in range(len(completeSuite)-1):
                        file.write("\nACTIVATION\n")
                        file.write('-'.join([f for f in completeSuite[j] if completeSuite[j+1][f] > 0 and completeSuite[j][f] < 0]))
                        file.write("\nDEACTIVATION\n")
                        file.write('-'.join([f for f in completeSuite[j] if completeSuite[j+1][f] < 0 and completeSuite[j][f] > 0]))
                    file.write("\nBREAKPOINT")
                    file.close()
                except Exception as e:
                    print(e)
                    print("Error when writing paths to text format in error isolation process. Process terminated.")
                    return

            discrepancies = TestingToolRunner.launch_test_oracle(controller, testing_tool_folder, feature_model_path, skip_generation=True, reference=reference+1, verbose=False)

            if not discrepancies:
                # all innocent
                if testing:
                    print("clearing culprit :(")
                all_suspects = [s for s in all_suspects if s not in transitions_under_test]
            else:
                if len(transitions_under_test) > 1:
                    number_of_divide += 1
                    # adding smaller groups to locate the culprit
                    groups.append(transitions_under_test[:round(len(transitions_under_test)/2)])
                    groups.append(transitions_under_test[round(len(transitions_under_test)/2):])
                else:
                    # culprit found. it has to stay in suspects, but the group is done.
                    culprits.append(transitions_under_test[0])
    if verbose:
        print("There were ", number_of_fails, " failures from the SMT solver.")
        print("There were ", number_of_divide, " divisions of suspects due to inconsistencies.")
    return culprits, uncoverableTransitions

def transitionIsPossible(transition, initialState):
    if (initialState[transition[0][0]] > 0 and transition[0][1] > 0) or (initialState[transition[0][0]] < 0 and transition[0][1] < 0):
        return False
    if (initialState[transition[1][0]] > 0 and transition[1][1] > 0) or (initialState[transition[1][0]] < 0 and transition[1][1] < 0):
        return False
    return True