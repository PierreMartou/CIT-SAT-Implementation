from OracleSolver import OracleSolver
from OraclePath import OraclePath
from SystemData import SystemData
from TestSuite import TestSuite, computeCITSuite, computeCTTSuite

models = "../data/RIS-FOP/"
s = SystemData(featuresFile=models + 'features.txt')
storage = models + "TestSuitesCIT/testSuite-"
t1 = computeCTTSuite(storage, 0, s, recompute=True)
t1suite = t1.getMinTestSuite()
startState = t1suite[0]
finalState = t1suite[1]
oracle = OracleSolver(s, steps=1)
path = oracle.createPath(startState, finalState)
print(path.getShortenedPath())


