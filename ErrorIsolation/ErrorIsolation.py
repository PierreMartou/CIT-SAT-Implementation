from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner
from TestOracle.OracleSolver import OracleSolver
from utils.SATSolver import SATSolver
from utils.TestSuite import computeCTTSuite
from CTT.CTT_heuristics import BuildingCTT
from utils.TestSuite import TestSuite
from utils.TestSuite import SystemData

def find_suspects(original_path, alt_path, step):
    suspects = []
    for path in [original_path, alt_path]:
        [activations, deactivations] = TestingToolRunner.activations_at_specific_step(step, path)
        features = ['+'+a for a in activations] + ['-'+d for d in deactivations]
        for i in range(len(features)):
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
    while groups:
        transitions_under_test = groups.pop()
        # create alternate path for group
        alt_exec = createAlternativePath(transitions_under_test, suspects, z3solver)
        if alt_exec is None:
            if len(transitions_under_test) > 1:
                groups.append(transitions_under_test[:round(len(transitions_under_test)/2)])
                groups.append(transitions_under_test[round(len(transitions_under_test)/2):])
            else:
                uncoverableTransitions.append(transitions_under_test[0])
                transitionsToCover.remove(possibleCoverage[0])
        else:
            paths.append(path)
            for t in possibleCoverage:
                currentCoverage.append(t)
    # At each valid group/alternative path found, execute it and either delete the transitions under test from suspects or divide groupings to find culprit among them !


    return False

def transitionIsPossible(transition, initialState):
    if (initialState[transition[0][1:]] > 0 and transition[0][:1] == '+') or (initialState[transition[0][1:]] < 0 and transition[0][:1] == '-'):
        return False
    if (initialState[transition[1][1:]] > 0 and transition[1][:1] == '+') or (initialState[transition[1][1:]] < 0 and transition[1][:1] == '-'):
        return False
    return True


def createAlternativePath(transition_under_test, suspects, solver):
    #algo for branching off paths

    possiblePathCoverage = [transition_under_test]
    currentCoverage = []
    uncoverableTransitions = []
    paths = []
    while len(possiblePathCoverage) > 0:
        possibleCoverage = possiblePathCoverage.pop()
        #path = solver.createPath(config1, config2, possibleCoverage)
        # create path with no initial/endstate and avoiding all suspects + transitions under test


