from pysat.solvers import Glucose3
from ManualCNFConversion import *
from ResultRefining import orderNodes
# For each constraint in a feature model, defines corresponding constraints for a SAT solver.


class PreSATSolver:
    def __init__(self, featureFile=None, mappingFile=None, contextsFile=None):
        self.features = []
        self.init_features(featureFile)

        self.contexts = []
        self.init_contexts(contextsFile)

        # Read file for constraints
        self.featureConstraints = [('root', 'Features', []),
                            ('mandatory', 'Features', ['MessageType', 'NotificationSystem', 'FriendFeature', 'ContactList']),
                            ('optional', 'Features', ['Mode']),
                            ('mandatory', 'MessageType', ['Textual']),
                            ('optional', 'MessageType', ['Photos', 'Vocals']),
                            ('alternative', 'NotificationSystem', ['Vibrator', 'Alarm', 'Mute']),
                            ('alternative', 'Mode', ['Standard', 'Lite']),
                            ('alternative', 'AddSystem', ['Match', 'Search']),
                            ('mandatory', 'FriendFeature', ['FriendName']),
                            ('optional', 'FriendFeature', ['Description', 'ProfilePicture']),
                            ('optional', 'ContactList', ['GroupFeature']),
                            ('mandatory', 'ContactList', ['AddSystem'])
                            ]

        self.contextConstraints = [('mandatory', 'Contexts', ['Environment', 'Age', 'Social']),
                                   ('optional', 'Contexts', ['Device Capabilities', 'Connection']),
                                   ('or', 'Device Capabilities', ['Handle Photos', 'Speakers']),
                                   ('alternative', 'Environment', ['In Pocket', 'Out Pocket']),
                                   ('alternative', 'Connection', ['Bad Connection', 'Good Connection']),
                                   ('alternative', 'In Pocket', ['Meeting', 'Loud']),
                                   ('alternative', 'Out Pocket', ['Night', 'Day']),
                                   ('alternative', 'Age', ['Teen', 'Adult']),
                                   ]

        self.mappingConstraints = []
        if mappingFile is not None:
            f = open(mappingFile, "r").readlines()
            for line in f:
                line = line.rstrip("\n")
                m_features = line.split('-IMPLIES-')[1].split('-')
                m_contexts = line.split('-IMPLIES-')[0].split('-')
                for c in m_contexts:
                    self.mappingConstraints.append(('mandatory', c, m_features))

        newFeatures = orderNodes(self.featureConstraints, 'Features')
        for f in self.features:
            if f not in newFeatures:
                print(f + " is not related to the features' root ?")
                newFeatures.append(f)
        self.features = newFeatures
        newContexts = orderNodes(self.contextConstraints, 'Contexts')
        for c in self.contexts:
            if c not in newContexts:
                print(c + " is not related to the contexts' root ?")
                newContexts.append(c)
        self.contexts = newContexts

        # we add a 'dummy' because a SAT solver begins at 1
        self.final_nodes = ['dummy', 'TreeRoot'] + self.contexts + self.features
        self.mappingConstraints.append(('root', 'TreeRoot', ['']))
        for (_, f1, list_f) in self.featureConstraints:
            if f1 not in self.features:
                print('Error in constraints : ' + f1 + ' is not a feature.')
                return
            for f2 in list_f:
                if f2 not in self.features:
                    print('Error in constraints : ' + f2 + ' is not a feature.')
                    return

        for (_, c1, list_c) in self.contextConstraints:
            if c1 not in self.contexts:
                print('Error in constraints : ' + c1 + ' is not a context.')
                return
            for c2 in list_c:
                if c2 not in self.contexts:
                    print('Error in constraints : ' + c2 + ' is not a context.')
                    return

        self.solver = Glucose3(incr=True)
        self.clauses = []
        for constraint in self.featureConstraints + self.mappingConstraints + self.contextConstraints:
            helper = switcher.get(constraint[0].lower(), lambda: print("Invalid constraint."))
            newClauses = helper(self.toIndex(constraint[1]), self.toIndex(constraint[2]))
            self.clauses = self.clauses + newClauses

        for clause in self.clauses:
            self.solver.add_clause(clause)

    def init_features(self, featureFile):
        if featureFile is None:
            self.features = self.features + ['Features', 'MessageType', 'Textual', 'Photos', 'Vocals',
                                             'NotificationSystem',
                                             'Vibrator', 'Alarm', 'Mute']
        else:
            f = open(featureFile, "r").readlines()
            for line in f:
                self.features = self.features + [line.split(' (#')[0]]

    def init_contexts(self, contextsFile):
        if contextsFile is None:
            print("No contexts provided.")
        else:
            f = open(contextsFile, "r").readlines()
            for line in f:
                self.contexts = self.contexts + [line.split(' (#')[0]]

    def toIndex(self, node):
        if isinstance(node, str):
            if node in self.final_nodes:
                return self.final_nodes.index(node)
            else:
                return 'VoidFeature'
        else:
            return [self.toIndex(f) for f in node]

    def printClauses(self):
        for clause in self.clauses:
            toPrint = []
            for el in clause:
                if el<0:
                    toPrint.append('- ' + self.final_nodes[abs(el)])
                else:
                    toPrint.append(self.final_nodes[abs(el)])
            print(toPrint)

    def getFeatures(self):
        return self.features.copy()

    def getContexts(self):
        return self.contexts.copy()

    def getContextConstraints(self):
        return self.contextConstraints.copy()

    def constructFactorsValues(self):
        valuesForFactors = {}
        for i in range(1, len(self.final_nodes)):
            valuesForFactors[self.final_nodes[i]] = [-i, i]
        return valuesForFactors

    def checkSAT(self, values=None):
        if values is None:
            values = []
        return self.solver.solve(assumptions=values)

    def getFeatureConstraints(self):
        return self.featureConstraints.copy()

