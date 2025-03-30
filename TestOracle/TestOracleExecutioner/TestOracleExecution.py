import os
import subprocess
import shutil
from Controller import Controller
class TestingToolRunner:

    @staticmethod
    def generate_tests(feature_model_path, testing_tool_folder, reference):
        executable_path = os.path.join(testing_tool_folder, "GenerationTestingTool")
        try:
            process = subprocess.Popen([executable_path, feature_model_path, str(reference), testing_tool_folder])
            process.wait()
            return True
        except (OSError, subprocess.SubprocessError) as e:
            print(f"Tool file was not found at specified path: {executable_path}")
            print(e)
            return False

    @staticmethod
    def execute_tests(controller, testing_tool_folder, reference):
        controller.disable_ui_view()

        first_path = os.path.join(testing_tool_folder, f"paths{reference}-0.txt")
        try:
            with open(first_path, 'r') as file:
                number_paths = int(file.readline())
        except IOError as e:
            print(e)
            return 0

        # Clear logs if they exist
        for i in range(number_paths):
            log_path = os.path.join(testing_tool_folder, f"logs{reference}-{i}.txt")
            if os.path.exists(log_path):
                with open(log_path, 'w') as file:
                    file.write('')

        # Process each path
        for j in range(number_paths):
            path = os.path.join(testing_tool_folder, f"paths{reference}-{j}.txt")
            try:
                with open(path, 'r') as file:
                    lines = file.readlines()

                activation_line = lines[4].strip()
                activations2 = activation_line.split("-")
                if lines[5].strip() != "DEACTIVATION":
                    print("Irregular pattern detected.")
                    return 0

                deactivation_line = lines[6].strip()
                deactivations2 = deactivation_line.split("-")
                controller.activate(deactivations2, activations2)

                step_counter = 0
                for line in lines[7:]:
                    line = line.strip()

                    if line == "ACTIVATION":
                        activation_line = next(file).strip()
                        activations = activation_line.split("-")
                        if next(file).strip() != "DEACTIVATION":
                            print("Irregular pattern detected.")
                            return 0
                        deactivation_line = next(file).strip()
                        deactivations = deactivation_line.split("-")
                        controller.activate(deactivations, activations)
                    elif line == "BREAKPOINT":
                        step_counter += 1
                        TestingToolRunner.write_state_to_file(controller, os.path.join(testing_tool_folder, f"logs{reference}-{j}.txt"))
            except IOError as e:
                print(e)
                return 0
        return number_paths

    @staticmethod
    def activations_at_specific_step(step, path):
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
            step_counter = 0
            for i in range(6):
                file.readline()

            for line in lines[6:]:
                line = line.strip()
                if step_counter == step:
                    activation_line = lines[i+1].strip()
                    activations = activation_line.split("-")
                    if lines[i+2].strip() != "DEACTIVATION":
                        print("Irregular pattern detected.")
                    deactivation_line = lines[i+3].strip()
                    deactivations = deactivation_line.split("-")
                    return [activations, deactivations]

                if line == "BREAKPOINT":
                    step_counter += 1
        except IOError as e:
            print(e)
            return None
        return None

    @staticmethod
    def verify_logs(testing_tool_folder, reference, number_paths):
        discrepancies = []

        all_logs = []
        for i in range(number_paths):
            log_path = os.path.join(testing_tool_folder, f"logs{reference}-{i}.txt")
            all_logs.append(TestingToolRunner.read_states_from_file(log_path))

        for i in range(len(all_logs[0])):
            current_logs = [log[i] for log in all_logs]
            first_log = current_logs[0]
            for j in range(1, len(current_logs)):
                next_log = current_logs[j]
                if TestingToolRunner.compare_logs(first_log, next_log):
                    discrepancy = f"\n ==================================================\nReference {reference}, at step {i}, between path 0 and alternative path {j}, logs are inconsistent.\n"
                    discrepancy += f"Logs: {first_log} VS {next_log}\n --------------------------------------------------"
                    discrepancies.append(discrepancy)
                    break
        if not discrepancies:
            discrepancies.append("All logs are consistent between alternative execution paths. Congratulations.")
        else:
            discrepancies[-1] += "\n =================================================="
        return discrepancies

    @staticmethod
    def read_states_from_file(file_path):
        logs = []
        current_logs = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line == "ENDSTATE":
                        logs.append(current_logs[:])
                        current_logs.clear()
                    elif line == "LINEMARKER":
                        current_logs.append(line)
                    else:
                        current_logs.append(line)
        except IOError as e:
            print(f"Error reading the logs from file: {e}")
            return None
        return logs

    @staticmethod
    def write_state_to_file(controller, filename):
        state = controller.get_state_as_log()

        # Ensure the log doesn't contain reserved keywords
        for line in state:
            if "ENDSTATE" in line or "LINEMARKER" in line:
                print(f"Error: Log contains reserved keywords (ENDSTATE or LINEMARKER), in: {line}")
                return

        try:
            with open(filename, 'a') as file:
                for line in state:
                    file.write(line + "\n")
                    file.write("LINEMARKER\n")
                file.write("ENDSTATE\n")
        except IOError as e:
            print(f"Error writing to file: {e}")
            raise e

    @staticmethod
    def compare_logs(logs1, logs2):
        set1 = set(logs1)
        set2 = set(logs2)
        return set1 != set2 or len(logs1) != len(logs2)

    @staticmethod
    def launch_test_oracle(controller, testing_tool_folder, feature_model_path, skip_generation, reference):
        if not skip_generation:
            success = TestingToolRunner.generate_tests(feature_model_path, testing_tool_folder, reference)
            if not success:
                print("Test generation failed.")
                return

        number_of_paths = TestingToolRunner.execute_tests(controller, testing_tool_folder, reference)
        discrepancies = TestingToolRunner.verify_logs(testing_tool_folder, reference, number_of_paths)
        for line in discrepancies:
            print(line)


controller = Controller()
reference = 0
skip_generation = False
TestingToolRunner.launch_test_oracle(controller, "./TestingTool/", "./src/features.txt", skip_generation, reference)
