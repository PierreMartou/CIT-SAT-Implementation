import sys
from utils import TestSuite
from TestOracle.AlternativePaths import AlternativePaths, computeAlts
from utils.SystemData import SystemData
from utils.TestSuite import computeCTTSuite

"""
CIT GENERATION
"""

# Generation
featuresFile = sys.argv[1] #"./features.txt" #
index = sys.argv[2] #"0"#
testingToolFolder = sys.argv[3] # "./" #
# featuresFile = "../data/RIS-FOP/" + 'features.txt'
s = SystemData(featuresFile=featuresFile)

# Reordering

# Test Suite Augmentation

"""
CTT GENERATION
"""

# Generation

# Parameters manipulation

"""
TEST ORACLE
"""

# Generation of alternative execution paths

# Execution

# State comparison