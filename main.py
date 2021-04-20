from CITSAT import CITSAT
from ResultRefining import printCoveringArray, numberOfChangements, orderArray
from UnifiedModel import SystemData
import time
from pysat.solvers import Glucose3
from TestsEvolution import TestsEvolution
from SATSolver import SATSolver
import math
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
    models = "./data/normal_size/"
    s = SystemData(models+'contexts.txt', models+'features.txt', models+'mapping.txt')
    result = CITSAT(s, False, 30)
    printCoveringArray(result, s, "Normal")
    print("================================REFINED MODE=====================================")
    printCoveringArray(result, s, "Refined")
    totalTime = time.time() - time1
    print("Computation time : " + str(totalTime) + " seconds")
    unrefinedCost = numberOfChangements(result, s.getContexts())
    print("COST UNREFINED : " + str(unrefinedCost))
    refinedCost = numberOfChangements(orderArray(result, s.getContexts()), s.getContexts())
    print("COST REFINED : " + str(refinedCost))
    print("Decrease in cost of : " + str((unrefinedCost - refinedCost)/unrefinedCost))


def multipleRuns(iterations):
    maxTime = 0
    minTime = 10000
    sumTime = 0
    iterations = 10
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
        testsEvolution = TestsEvolution("testsFile.txt", s, mode=mode)
    else:
        toAdd = ["AddSystem/Alternative/Match-Search"]# , "FriendFeature/Optional/Description-ProfilePicture"]
        testsEvolution = TestsEvolution("testsFile.txt", s, mode=toAdd)
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

def rearrangementMetricsTest(iterations):
    models = ["./data/minimalist/", "./data/normal_size/", "./data/enlarged/"]
    unrefinedScore = 0
    refinedScore = 0
    increaseScore = 0
    tmpUnrefinedVariance = 0
    tmpRefinedVariance = 0
    tmpIncreaseVariance = 0
    for model in models:
        for i in range(iterations):
            s = SystemData(model + 'contexts.txt', model + 'features.txt', model + 'mapping.txt')
            result = CITSAT(s, False, 30)
            unrefined = numberOfChangements(result, s.getContexts())
            unrefinedScore += unrefined
            tmpUnrefinedVariance += unrefined * unrefined
            refined = numberOfChangements(orderArray(result, s.getContexts()), s.getContexts())
            refinedScore += refined
            tmpRefinedVariance += refined * refined
            increase = 100*(unrefined - refined) / unrefined
            increaseScore += increase
            tmpIncreaseVariance += increase * increase

    print("Unrefined score : " + str(unrefinedScore) + "; in average : " + str(unrefinedScore/(3*iterations)))
    print("Refined score : " + str(refinedScore) + "; in average : " + str(refinedScore/(3*iterations)))
    print("On average, a decrease of " + str(100*(unrefinedScore - refinedScore)/unrefinedScore) + " %")
    print("Increase score on average : " + str(increaseScore/(3*iterations)) + " %")
    print("Variance of the score : " + str(math.sqrt(tmpIncreaseVariance/(3*iterations) - ((increaseScore/(3*iterations)) * (increaseScore/(3*iterations))))))

# rearrangementMetricsTest(10)
# anotherTest()
# incrementalRun("SAT")
singleRun() # Runs a single time the algorithm and displays the results

# multipleRuns(3) # Runs multiple times the algorithm, in order to obtain the average computation time

# thesisExample() # To illustrate covering array, we used this example