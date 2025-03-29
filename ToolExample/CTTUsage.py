from utils.TestSuite import computeCTTSuite

folder = "./ToolExample/"
system = "./ToolExample/features.txt"

# computes a test suite with full interaction coverage and stores it in the given folder. Does not recompute it if there is already a test suite at this place.
generated_test_suite = computeCTTSuite(folder, system, iteration=0, recompute=False)