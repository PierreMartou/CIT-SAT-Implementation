import re

class SystemData:
    def __init__(self, contextsFile=None, featuresFile=None, mappingFile=None):
        if featuresFile is None:
            featuresFile = 'features.txt'
        if contextsFile is None:
            contextsFile = 'contexts.txt'
        if mappingFile is None:
            mappingFile = 'mapping.txt'

        # Read files for nodes
        self.features = []
        self.initFeatures(featuresFile)

        self.contexts = []
        self.initContexts(contextsFile)

        # Read file for constraints
        self.featureConstraints = []
        self.initFeatureConstraint(featuresFile)

        self.contextConstraints = []
        self.initContextConstraint(contextsFile)

        # Read mapping file
        self.mappingConstraints = []
        self.initMapping(mappingFile)

        # We add a 'dummy' because a SAT solver begins at 1
        self.finalNodes = ['dummy', 'TreeRoot'] + list(self.contexts) + list(self.features)
        self.allConstraints = [('root', 'TreeRoot',[''])]\
                              + self.featureConstraints + self.contextConstraints + self.mappingConstraints

        # This is the data structure CITSAT.py uses
        self.valuesForFactors = {}
        index = 1
        for node in self.finalNodes[1:]:
            self.valuesForFactors[node] = [index, -index]
            index += 1

    def initFeatures(self, featureFile):
        if featureFile is None:
            print("No features provided.")
            self.features = []
        else:
            f = open(featureFile, "r").readlines()
            self.features = set()
            for line in f:
                index =0
                for feature in re.split("[\-/]", line):
                    if index != 1:
                        self.features.add(feature.replace("\n", ""))
                    index+=1

    def initContexts(self, contextsFile):
        if contextsFile is None:
            print("No contexts provided.")
            self.contexts = []
        else:
            f = open(contextsFile, "r").readlines()
            self.contexts = set()
            for line in f:
                index = 0
                for context in re.split("[\-/]", line):
                    if index != 1:
                        self.contexts.add(context.replace("\n", ""))
                    index += 1

    def initFeatureConstraint(self, featuresFile):
        if featuresFile is None:
            print("No constraints provided for features.")
            self.featureConstraints = []
        else:
            f = open(featuresFile, "r").readlines()
            self.featureConstraints = [('root', 'Features', [])]
            for line in f:
                parsedLine = line.replace("\n", "").split("/")
                newConstraint = (parsedLine[1], parsedLine[0], parsedLine[2].split("-"))
                self.featureConstraints.append(newConstraint)

    def initContextConstraint(self, contextFile):
        if contextFile is None:
            print("No constraints provided for contexts.")
            self.contextConstraints = []
        else:
            f = open(contextFile, "r").readlines()
            self.contextConstraints = [('root', 'Contexts', [])]
            for line in f:
                parsedLine = line.replace("\n", "").split("/")
                newConstraint = (parsedLine[1], parsedLine[0], parsedLine[2].split("-"))
                self.contextConstraints.append(newConstraint)

    def initMapping(self, mappingFile):
        if mappingFile is None:
            print("No mapping provided.")
            self.mappingConstraints = []
        else:
            f = open(mappingFile, "r").readlines()
            activatesFeature = {}
            for line in f:
                line = line.rstrip("\n")
                m_features = line.split('-IMPLIES-')[1].split('-')
                m_contexts = line.split('-IMPLIES-')[0].split('-')
                #for c in m_contexts:
                #    self.mappingConstraints.append(('mandatory', c, m_features))
                for f in m_features:
                    if len(m_contexts) == 1:  # maybe extend later
                        if f in activatesFeature:
                            activatesFeature[f].append(m_contexts[0])
                        else:
                            activatesFeature[f] = [m_contexts[0]]
                    self.mappingConstraints.append(('onePositiveRawClause', f, m_contexts))
                    if len(m_contexts) > 1:
                        for c in m_contexts:
                            self.mappingConstraints.append(('onePositiveRawClause', c, [f]))

            for feature in activatesFeature:
                self.mappingConstraints.append(('oneNegativeRawClause', feature, activatesFeature[feature]))


    def toIndex(self, node):
        if isinstance(node, str):
            if node in self.finalNodes:
                return self.finalNodes.index(node)
            else:
                # For example, the Root constraint does not contain any child features, he will search an empty string.
                return 'VoidFeature'
        else:
            return [self.toIndex(f) for f in node]

    def getFeatures(self):
        return list(self.features.copy())

    def getContexts(self):
        return list(self.contexts.copy())

    def getNodes(self):
        return self.finalNodes.copy()

    def getConstraints(self):
        return self.allConstraints.copy()

    def getValuesForFactors(self):
        return self.valuesForFactors.copy()
