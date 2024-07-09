# Reads "features.txt" in argument / creates execution paths
import sys
from utils import TestSuite
from oracle.AlternativePaths import AlternativePaths, computeAlts
from utils.SystemData import SystemData
from utils.TestSuite import computeCTTSuite

if len(sys.argv) < 2:
    print("An argument that precises the file name where the feature model is stored is missing.")

featuresFile = sys.argv[1]
# featuresFile = "../data/RIS-FOP/" + 'features.txt'
s = SystemData(featuresFile=featuresFile)
iteration = ""
print("Step 1/2: Generating test suite")

testsuite = computeCTTSuite("./testsuite", iteration, s, recompute=True, verbose=True)

print("Step 2/2: Generating execution paths")
paths, undetectables = computeAlts("./paths", s, testsuite.getUnorderedTestSuite(), iteration, states=4, recompute=True, verbose=True)
print("Finished generation of execution paths.")
# In Java : read execution paths and create logs

# read logs and find differences. If they were differences, print the faulty transition & alternative path which is different & highlight difference

#differences = []
#if differences:
#    print("Differences were found. They are catalogued in differences.txt (don't forget to save this file and send it to us !).")
