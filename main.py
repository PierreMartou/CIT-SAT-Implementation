from CITSAT import CITSAT
from ResultRefining import printCoveringArray
from UnifiedModel import SystemData
import time
from pysat.solvers import Glucose3
from TestsEvolution import TestsEvolution
from SATSolver import SATSolver
"""Uses CITSAT() and displays the results.
"""
def testCITSATData():
    s = SystemData('contexts.txt', 'features.txt', 'mapping.txt')
    result = CITSAT(s, False)
    printCoveringArray(result, s, "Normal")
    print("================================REFINED MODE=====================================")
    printCoveringArray(result, s, "Refined")

def singleRun():
    time1 = time.time()
    models = "./data/minimalist/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    result = CITSAT(s, False, 30)
    printCoveringArray(result, s, "Normal")
    print("================================REFINED MODE=====================================")
    printCoveringArray(result, s, "Refined", True)
    totalTime = time.time() - time1
    print("Computation time : " + str(totalTime) + " seconds")


def multipleRuns(iterations):
    maxTime = 0
    minTime = 10000
    sumTime = 0
    iterations = 1
    for i in range(iterations):
        time1 = time.process_time()
        testCITSATData()
        totalTime = time.process_time() - time1
        maxTime = max(totalTime, maxTime)
        minTime = min(totalTime, minTime)
        sumTime += totalTime
        print(str(i) + "nth iteration. Computation took " + str(totalTime) + " seconds.")

    print("We took " + str(sumTime) + " seconds to compute " + str(iterations) + ".")
    print("The maximum time is " + str(maxTime) + " seconds.")
    print("The minimum time is " + str(minTime) + " seconds.")

def thesisExample():
    example = {}
    example['Brand'] = ['Nokia', 'Samsung']
    example['State'] = ['Broken', 'Used', 'New']
    example['Performance'] = ['Slow', 'Fast']
    result = CITSAT(None, example, False)
    for testCase in result:
        print(testCase)


def incrementalRun(mode="SAT"):
    time1 = time.time()
    models = "./data/normal_size/"
    s = SystemData(models + 'contexts.txt', models + 'features.txt', models + 'mapping.txt')
    if mode in "SAT":
        testsEvolution = TestsEvolution("testsFile.txt", s, SATSolver(s), mode=mode)
    else:
        toAdd = ["AddSystem/Alternative/Match-Search", "FriendFeature/Optional/Description-ProfilePicture"]
        testsEvolution = TestsEvolution("testsFile.txt", s, SATSolver(s), mode=toAdd)
    result = CITSAT(s, False, 30, testsEvolution)
    # printCoveringArray(result, s, "Normal", False, testsEvolution)
    print("================================REFINED MODE=====================================")
    printCoveringArray(result, s, "Refined", False, testsEvolution)
    totalTime = time.time() - time1
    print("Computation time : " + str(totalTime) + " seconds")


def myLittleTests():
    g = Glucose3(incr=True)
    g.add_clause([1, 2], [3, 4])
    print(g.propagate([-1, 3]))

def anotherTest():
    s = SystemData('contexts.txt', 'features.txt', 'mapping.txt')
    mySat = SATSolver(s)
    (_, propagated) = mySat.propagate([s.toIndex("Night")])
    for p in propagated:
        print(s.getNodes()[abs(p)])

#anotherTest()
incrementalRun("feature")
#singleRun() # Runs a single time the algorithm and displays the results

# multipleRuns(3) # Runs multiple times the algorithm, in order to obtain the average computation time

# thesisExample() # To illustrate covering array, we used this example