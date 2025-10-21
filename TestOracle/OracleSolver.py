from utils.SystemData import SystemData
from z3 import *
from utils.ManualCNFConversion import *
from utils.TestSuite import TestSuite

def firstTry():
    o = Optimize()
    x = Int('xez-0')
    o.add(And(x > 0, x < 5))
    y = Bool('Low')
    o.add(Implies(y, (x < 4)))
    o.assert_exprs(y)

    o.maximize(x)
    print(o.check())  # prints sat
    print(o.model())  # prints [x = 4]


class OracleSolver:
    def __init__(self, systemData, states):

        self.s = systemData
        self.solver = Optimize()
        self.clauses = []
        self.featuresInStates = []

        self.startFeatures = self.addState("start")
        self.finalFeatures = self.addState("final")
        self.allFeatures = {}
        for i in range(states):
            self.featuresInStates.append(self.addState(i))
            self.allFeatures[i] = self.featuresInStates[i]

        self.allFeatures['start'] = self.startFeatures
        self.allFeatures['final'] = self.finalFeatures

        self.objective = self.createObjectives()
        self.solver.push()

    def featureID(self, f, state):
        return f+"#"+str(state)

    def addState(self, state):
        features = {}
        dummyCount = 0
        for feature in self.s.getNodes():
            if "#" in feature:
                print("warning, symbol # is not allowed in features")
            if feature != "dummy":
                features[feature] = Bool(self.featureID(feature, state))
            else:
                dummyCount += 1
        if dummyCount > 1:
            print("error in oracle solver: multiple dummies found")
        for constraint in self.s.getConstraints():
            helper = switcher.get(constraint[0].lower(), lambda: print("Invalid constraint."))
            newClauses = helper(self.s.toIndex(constraint[1]), self.s.toIndex(constraint[2]))
            self.clauses = self.clauses + newClauses
        # Adding clauses already in CNF form.
        self.clauses = self.clauses + self.s.getCNFConstraints()

        for clause in self.clauses:
            #if state == "start":
            #    print(clause)
            #print([abs(clause[i]) for i in range(len(clause))])
            #print([features[abs(clause[i])] for i in range(len(clause))])
            clauseFeatures = []
            nodes = self.s.getNodes()
            for f in clause:
                if f > 0:
                    clauseFeatures.append(features[nodes[f]])
                else:
                    clauseFeatures.append(Not(features[nodes[abs(f)]]))
            self.solver.add(Or(clauseFeatures))

        return features

    def minPathObjective(self):
        equalStateVariables = []

        equalStateVariable = Int("EqualStateVariable#start")
        equalStateVariables.append(equalStateVariable)
        self.solver.add(If(And([self.finalFeatures[f] == self.startFeatures[f] for f in self.finalFeatures]),
                           equalStateVariable == 0, equalStateVariable == 1))

        for state in range(len(self.featuresInStates)):
            equalStateVariable = Int("EqualStateVariable#"+str(state))
            equalStateVariables.append(equalStateVariable)
            self.solver.add(If(And([self.finalFeatures[f] == self.featuresInStates[state][f] for f in self.finalFeatures]), equalStateVariable == 0, equalStateVariable == 1))

        numberOfSteps = Int("NumberOfSteps")
        self.solver.add(numberOfSteps == sum(equalStateVariables))
        return numberOfSteps

    def minCostObjective(self):
        equalValueVariables = []
        states = ['start'] + [i for i in range(len(self.featuresInStates))] + ['final']
        for i in range(len(states)-1):
            currentState = self.allFeatures[states[i]]
            futureState = self.allFeatures[states[i+1]]
            for f in currentState:
                equalValueVariable = Int("EqualValueVariable#"+str(f)+"#"+str(states[i]))
                self.solver.add(If(currentState[f] == futureState[f], equalValueVariable == 0, equalValueVariable == 1))
                equalValueVariables.append(equalValueVariable)

        cost = Int("Cost")
        self.solver.add(cost == sum(equalValueVariables))
        return cost

    def createObjectives(self):
        obj1 = self.minPathObjective()
        obj2 = self.minCostObjective()
        # obj3 = weighted sum of obj1 and obj2
        # return obj3
        return obj1, obj2


    def setState(self, featureStates, values):
        #print("\nhere are the values :",values)
        for f in values:
            #nodes = self.s.getNodes()
            #print(nodes[abs(values[f])])
            #print(featureStates[f], " of value ", values[f])
            if values[f] > 0:
                #self.solver.assert_exprs(featureStates[f])
                self.solver.add(featureStates[f])
            else:
                self.solver.add(Not(featureStates[f]))
                #self.solver.assert_exprs(Not(featureStates[f]))

    def createPath(self, initConfig, finalConfig, forbiddenTransitions, satisOnly=False, mandatoryTransitions = None, startupConfig=None):
        self.solver.pop()
        self.solver.push()
        # add initial configuration to constraints
        if initConfig:
            self.setState(self.startFeatures, initConfig)

        # add final configuration to constraints
        if finalConfig:
            self.setState(self.finalFeatures, finalConfig)

        # add contraints on transitions
        self.forbidAllTransitions(forbiddenTransitions)

        # if there is a startup configuration, we must forbid transitions from this configuration to initial configuration.
        if startupConfig:
            startupState = {}
            for f in startupConfig:
                startupState[f] = Bool(self.featureID(f, "startup"))

            self.setState(startupState, startupConfig)

            for transition in forbiddenTransitions:
                self.forbidTransition(transition, startupState, self.startFeatures)

        #need specific transitions to exist
        if mandatoryTransitions:
            self.mustHaveTransitions(mandatoryTransitions)

        # order in self.objective is important since z3 optimises in lexicographic manner.
        for o in self.objective:
            self.solver.minimize(o)
        satModel = self.solver.check()
        if satisOnly:
            return satModel

        if satModel == unsat:
            return None

        values = self.solver.model()
        states = [{} for i in range(len(self.featuresInStates))]
        new_init_config = {}
        new_final_config = {}
        for solverFeature in values:
            spl = str(solverFeature).split("#")
            #print(spl)
            if len(spl) == 2:
                feature, state = spl
                #print(feature, state, values[solverFeature])
                if state not in ["start", "final", "startup"] and feature not in ["EqualStateVariable"]:
                    state = int(state)
                    states[state][feature] = self.s.toIndex(feature) if values[solverFeature] else -self.s.toIndex(feature)

                if state == "start" and initConfig is None and feature not in ["EqualStateVariable"]:
                    new_init_config[feature] = self.s.toIndex(feature) if values[solverFeature] else -self.s.toIndex(feature)

                if state == "final" and finalConfig is None and feature not in ["EqualStateVariable"]:
                    new_final_config[feature] = self.s.toIndex(feature) if values[solverFeature] else -self.s.toIndex(feature)

        if initConfig is None:
            initConfig = new_init_config

        if finalConfig is None:
            finalConfig = new_final_config

        return TestSuite(self.s, [initConfig] + states + [finalConfig])

    def forbidAllTransitions(self, forbiddenTransitions):
        sequenceOfStates = [self.startFeatures] + self.featuresInStates + [self.finalFeatures]
        for transition in forbiddenTransitions:
            for i in range(len(sequenceOfStates)-1):
                self.forbidTransition(transition, sequenceOfStates[i], sequenceOfStates[i+1])

    def forbidTransition(self, transition, initState, nextState):
        clause = []
        for f in transition:
            featureName = f[0]
            if f[1] > 0:
                clause.append(initState[featureName])
                clause.append(Not(nextState[featureName]))
            else:
                clause.append(Not(initState[featureName]))
                clause.append(nextState[featureName])
        self.solver.add(Or(clause))

    def preprocessTransitions(self, allTransitions):
        decomposables = []
        nonDecomposables = []
        for t in allTransitions:
            #indexedT = [self.s.toIndex(f[1:]) if f[0:1] == '+' else -self.s.toIndex(f[1:]) for f in t]
            if self.decomposableTransition(t):
                decomposables.append(t)
            else:
                nonDecomposables.append(t)
        return decomposables, nonDecomposables

    def decomposableTransition(self, transition):
        initState = {}
        finalState = {}
        for f in transition:
            initState[f[0]] = -1*f[1]
            finalState[f[0]] = f[1]
        path = self.createPath(initState, finalState, [transition], satisOnly=True)
        if path == unsat:
            return False
        else:
            return True

    # Accepts transition in the form ((a, 1), (b, -1))
    def mustHaveTransitions(self, mandatoryTransitions):
        states = ['start'] + [i for i in range(len(self.featuresInStates))] + ['final']
        for transition in mandatoryTransitions:
            transitionClause = []
            for i in range(len(states)-1):
                stateClause = []
                currentState = self.allFeatures[states[i]]
                futureState = self.allFeatures[states[i+1]]
                for f in transition:
                    if f[1] > 0:
                        stateClause.append(Not(currentState[f[0]]))
                        stateClause.append(futureState[f[0]])
                    else:
                        stateClause.append(currentState[f[0]])
                        stateClause.append(Not(futureState[f[0]]))
                # If this condition is fullfilled, the transition is covered by currentstate -> futurestate.
                transitionClause.append(And(stateClause))
            # the transition is covered at least once.
            self.solver.add(Or(transitionClause))
