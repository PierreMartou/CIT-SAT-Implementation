# Reads "features.txt" in argument / creates execution paths
import sys
from utils import TestSuite
from oracle.AlternativePaths import AlternativePaths, computeAlts
from utils.SystemData import SystemData
from utils.TestSuite import computeCTTSuite

if len(sys.argv) < 3:
    print("An argument with the path to the feature model, or the index of the test suite, is missing.")

if len(sys.argv) < 2:
    print("The arguments with the path to the feature model and the index the test suite are missing.")

featuresFile = "./features.txt" #sys.argv[1] #
index = "0"#sys.argv[2] #
# featuresFile = "../data/RIS-FOP/" + 'features.txt'
s = SystemData(featuresFile=featuresFile)

for feature in s.getFeatures():
    if feature in ["ACTIVATION", "DEACTIVATION", "BREAKPOINT"]:
        print("!!!!WARNING : reserved keywords are used in the name of features (ACTIVATION, DEACTIVATION, BREAKPOINT). Please modify them to prevent this.")


iteration = ""
print("Step 1/2: Generating test suite")

testsuite = computeCTTSuite("./testsuite"+str(index), iteration, s, recompute=True, verbose=True)

print("Step 2/2: Generating execution paths")
paths, undetectables = computeAlts("./paths"+str(index), s, testsuite.getUnorderedTestSuite(), iteration, states=4, recompute=True, verbose=True)

paths = [[p.getUnorderedTestSuite() for p in path] for path in paths]
allFiles = []
largestNAlternatives = 0
originalTestSuite = testsuite.getUnorderedTestSuite()
originalPath = [[originalTestSuite[i], originalTestSuite[i+1]] for i in range(len(originalTestSuite)-1)]
updatedPaths = [[originalPath[i]] + paths[i] for i in range(len(originalPath))]
for nCurrent in range(len(updatedPaths)):
    if len(updatedPaths[nCurrent]) > largestNAlternatives:
        largestNAlternatives = len(updatedPaths[nCurrent])

try:
    for i in range(largestNAlternatives):
        filePath = "./paths" + str(index) + "-" + str(i) + ".txt"
        f = open(filePath, "w")
        f.write(str(largestNAlternatives)+"\n")
        f.write(str(undetectables) + "% undetectables")
        allFiles.append(f)

    for step in range(len(updatedPaths)):
        path = updatedPaths[step]
        for i in range(largestNAlternatives):
            parallelI = i
            if parallelI >= len(path):
                parallelI = 0
            f = allFiles[i]
            parallelPath = path[parallelI]
            #if type(parallelPath) is TestSuite:
            #    parallelPath = parallelPath.getUnorderedSuite()
            prevConfig = parallelPath[0]
            for config in parallelPath[1:]:
                changes = [f for f in prevConfig if prevConfig[f] != config[f]]
                f.write("\nACTIVATION\n")
                f.write('-'.join([f for f in changes if config[f] > 0]))
                f.write("\nDEACTIVATION\n")
                f.write('-'.join([f for f in changes if config[f] < 0]))

                prevConfig = config
            f.write("\nBREAKPOINT")

    for f in allFiles:
        f.close()
except Exception as e:
    print(e)
    print("Error when writing paths to text format, at step " + str(step), ", alternative number " + str(i))


print("Finished generation of execution paths.")
# In Java : read execution paths and create logs

# read logs and find differences. If they were differences, print the faulty transition & alternative path which is different & highlight difference

#differences = []
#if differences:
#    print("Differences were found. They are catalogued in differences.txt (don't forget to save this file and send it to us !).")
