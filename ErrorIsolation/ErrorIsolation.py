from TestOracle.TestOracleExecutioner.TestOracleExecution import TestingToolRunner

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

def naive_approach(suspects):
    return False

def dichotomic_approach():
    return False
