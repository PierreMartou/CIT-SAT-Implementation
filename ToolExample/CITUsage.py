from utils.TestSuite import computeCITSuite


folder = "./ToolExample/"
system = "./ToolExample/features.txt"
# computes a test suite with full interaction coverage and stores it in the given folder. Does not recompute it if there is already a test suite at this place.
generated_test_suite = computeCITSuite(folder, system, iteration=0, recompute=False)

# gets the test suite in a particular order.
# The four reorderings are: "getMinTestSuite" (feature activations minimised),
# "getMaxTestSuite" (dissimilarity maximised),
# 'getRandomTestSuite" (random order),
# 'getUnorderedTestSuite" (no reordering after generation).

reordered_test_suite = generated_test_suite.getMinTestSuite()
