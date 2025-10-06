from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner
from TestOracle.OracleSolver import OracleSolver
from utils.SATSolver import SATSolver
from utils.TestSuite import computeCTTSuite

def find_suspects(original_path, alt_path, step):
    suspects={}
    for path in [original_path, alt_path]:
        [activations, deactivations] = TestingToolRunner.activations_at_specific_step(step, path)
        features = ['+'+a for a in activations] + ['-'+d for d in deactivations]
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                # ordering
                if features[i][1:] < features[j][1:]:
                    suspects += (features[i], features[j])
                else:
                    suspects += (features[j], features[i])

    return suspects

def error_isolation(system_data, original_path, alt_path, step, states = 4):
    #will be used to find initial states
    satsolver = SATSolver(system_data)

    #will be used to find alternative paths
    z3solver = OracleSolver(system_data, states)

    # step 1 : find suspects
    suspects = find_suspects(original_path, alt_path, step)

    # step 2 : create biggest valid groups. Aim for biggest, then biggest with the rest until all suspects are in a group. Can use CTT principles for that ?


    # step 3 : reuse alternative paths algorithms to create alt paths, dichotomic search, but forbid all transitions still in the suspects.
    # At each valid group/alternative path found, execute it and either delete the transitions under test from suspects or divide groupings to find culprit among them !


    return False

def dichotomic_approach():
    return False
