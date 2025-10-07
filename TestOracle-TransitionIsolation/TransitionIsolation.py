import os
from itertools import combinations

def add_to_suspects(suspects, act, deact):
    tagged_act = [f'+{a}' for a in act]
    tagged_deact = [f'-{d}' for d in deact]

    for pair in combinations(tagged_act, 2):
        suspects.add(tuple(sorted(pair)))

    for pair in combinations(tagged_deact, 2):
        suspects.add(tuple(sorted(pair)))

    for a in tagged_act:
        for d in tagged_deact:
            suspects.add(tuple(sorted((a, d))))

def identifySuspects(testing_folder, reference, alt_path_number, transition_number):
    suspects = set
    first_path = os.path.join(testing_folder, f"paths{reference}-0.txt")

    """try:
        with open(first_path, 'r') as file:
            number_paths = int(file.readline())
    except IOError as e:
        print(e)
        return 0"""

    alt_path = os.path.join(testing_folder, f"paths{reference}-{alt_path_number}.txt")
    try:
        with open(first_path, 'r') as file:
            lines = file.readlines()

            activation_line = lines[3].strip()
            activations2 = activation_line.split("-")
            if lines[4].strip() != "DEACTIVATION":
                print("Irregular pattern detected in " + first_path + ", should have DEACTIVATION instead of " + lines[5].strip())
                return 0

            if transition_number == 0:
                deactivation_line = lines[5].strip()
                deactivations2 = deactivation_line.split("-")
                #controller.activate(deactivations2, activations2)
                add_to_suspects(suspects, activations2, deactivations2)

            step_counter = 0
            line_counter = 6
            for line in lines[6:]:
                line = line.strip()

                if line == "ACTIVATION":
                    activation_line = lines[line_counter + 1].strip()
                    activations = activation_line.split("-")
                    if lines[line_counter + 2].strip() != "DEACTIVATION":
                        print("Irregular pattern detected.")
                        return 0
                    deactivation_line = lines[line_counter + 3].strip()
                    deactivations = deactivation_line.split("-")
                    if transition_number == line_counter:
                        # controller.activate(deactivations, activations)
                        add_to_suspects(suspects, activations, deactivations)
                elif line == "BREAKPOINT":
                    step_counter += 1
                    #TestingToolRunner.write_state_to_file(controller, os.path.join(testing_tool_folder, f"logs{reference}-{j}.txt"))
                line_counter += 1
    except IOError as e:
        print(e)
        return 0
    return suspects

def linear_elimination(suspects):
    for suspect in suspects:
        pass
        # init state

# gives out a list of either suspect or even culprit