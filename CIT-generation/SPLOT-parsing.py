
def writeTextFiles(filename):
    featureModel, constraints = getContents(filename)
    txtFilename = filename.replace("xml", "txt").replace("source", "txt")
    txtFile = open(txtFilename, "w")

    for index in range(len(featureModel)-1):
        relations = getRelation(featureModel, index)
        for relation in relations:
            txtFile.write(relation+"\n")

    constraintFileName = filename.replace("xml", "txt").replace("source", "txt-constraints")
    constraintFile = open(constraintFileName, "w")

    for index in range(len(constraints)):
        constraint = getConstraint(constraints, index)
        constraintFile.write(constraint)

def getContents(filename):
    file = open(filename, "r")
    content = file.readlines()
    startFM = 0
    line = content[startFM]
    while line != "<feature_tree>\n":
        startFM += 1
        line = content[startFM]
    endFM = startFM
    while line != "</feature_tree>\n":
        endFM += 1
        line = content[endFM]
    featureModel = content[startFM+1:endFM]

    root = findUniqueID(featureModel[0])
    featureModel[0] = featureModel[0].replace(root, 'Feature')

    startConstraint = endFM + 1
    endConstraint = startConstraint
    constraints = []
    while line != "</constraints>\n":
        endConstraint += 1
        line = content[endConstraint]
        if root in line.split("OR"):
            pass
            #do something here
        constraints.append(line)
    constraints = content[startConstraint+1:endConstraint]
    return featureModel, constraints


def getConstraint(constraints, index):
    return constraints[index].split(":")[1]


def getRelation(featureModel, index):
    line = featureModel[index]
    parent = findUniqueID(line)
    relations = []

    level = line.count("\t")
    tempIndex = index + 1
    tempLine = featureModel[tempIndex]
    tempLevel = tempLine.count("\t")

    if tempLine.replace("\t", "")[:2] == ": ":
        return []

    while tempLevel > level and tempIndex < len(featureModel):
        if tempLevel == level + 1:
            relationType = tempLine.replace("\t", "")[:2]
            if relationType == ":o":
                relations.append(parent+"/Optional/"+findUniqueID(tempLine))
            elif relationType == ":m":
                relations.append(parent+"/Mandatory/"+findUniqueID(tempLine))
            elif relationType == ":g":
                relationType = "Alternative" if line[line.find("[")+1:line.find("]")] == "1,1" else "Or"
                relation = parent + "/" + relationType + "/"
                orIndex = tempIndex + 1
                orLine = featureModel[orIndex]
                orLevel = orLine.count("\t")
                while orLevel > tempLevel and orIndex < len(featureModel):
                    if orLevel == tempLevel + 1:
                        if orLine.replace("\t", "")[:2] != ": ":
                            print("ERROR WHILE PARSING ALTERNATIVE/OR CONSTRAINTS.")
                        relation += findUniqueID(orLine) + "-"
                    orIndex += 1
                    if orIndex < len(featureModel):
                        orLine = featureModel[orIndex]
                    orLevel = orLine.count("\t")
                relations.append(relation[:-1])
            else:
                print("ERROR IN PARSING XML FILE. FOUND : " + str(relationType))
        tempIndex += 1
        if tempIndex < len(featureModel):
            tempLine = featureModel[tempIndex]
        tempLevel = tempLine.count("\t")
    return relations


def getOneLevelBelow(featureModel, line):
    pass


def findUniqueID(line):
    return line[line.find("(")+1:line.find(")")]


# getSystemData("../data/SPLOT/SPLOT-source/SPLOT-3CNF-FM-500-50-1.00-SAT-10.xml")
writeTextFiles("../data/SPLOT/SPLOT-source/model_20110516_1331478109.xml")
