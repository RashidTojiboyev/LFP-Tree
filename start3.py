class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None  # link similar nodes
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):  # DFS to print tree
        print(' ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)


"""if __name__=='__main__':
    rootNode=treeNode('pyramid',1,None)
    rootNode.children['eye']=treeNode('eye',1,None)
    rootNode.children['phoenix']=treeNode('phoenix',1,None)
    #rootNode.disp()
    print('rootNode.disp()=', rootNode.disp())"""

def createTree(dataSet, minSup=1):
    headerTable = {}

    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]

    for k in list(headerTable):
        if headerTable[k] < minSup:
            del (headerTable[k])

    freqItemSet = set(headerTable.keys())

    if len(freqItemSet) == 0:
        return None, None

    for k in headerTable:
        headerTable[k] = [headerTable[k], None]

    retTree = treeNode('Null Set', 1, None)

    for tranSet, count in dataSet.items():
        localD = {}

        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0]

        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)
            return retTree, headerTable


def updateTree(items, inTree, headerTable, count):

    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count)
    else:
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:
           headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])

    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink

    nodeToTest.nodeLink = targetNode


def loadSimpDat():
    simpDat = [['s3', 's2', 'n6', 's4', 's5'],
               ['s3', 'n6', 'e4', 'e5'],
               ['s3','s2','e4','e5'],
               ['s3', 's2', 'n6'],
               ['s3', 's2', 'n6', 's4', 's5']]

    simpDat1 = [ ['r', 'z', 'h', 'j', 'p'],
                ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
                ['z'],
                ['r', 'x', 'n', 'o', 's'],
                ['y', 'r', 'x', 'z', 'q', 't', 'p'],
                ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simpDat


def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict

"""if __name__=='__main__':
    simpDat=loadSimpDat()
    print('simpDat=',simpDat)
    initSet=createInitSet(simpDat)
    print('initSet=',initSet)
    myFPtree,myHeaderTab=createTree(initSet,3)
    myFPtree.disp()"""


def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)


def findPrefixPath(basePat, treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

"""if __name__=='__main__':

    simpDat=loadSimpDat()
    initSet=createInitSet(simpDat)
    myFPtree,myHeaderTab=createTree(initSet,3)
    #print('myFPtree=',myFPtree)
    #print('myHeaderTab=',myHeaderTab)
    print('s3 base:',findPrefixPath('s3', myHeaderTab['s3'][1]))
    print('s2 base:',findPrefixPath('s2', myHeaderTab['s2'][1]))
    print('n6 base:',findPrefixPath('n6', myHeaderTab['n6'][1]))
    print('s4 base:',findPrefixPath('s4', myHeaderTab['s4'][1]))"""


def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: str(p[1]))]
    for basePat in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        print('finalFrequent Item: ', newFreqSet)
        freqItemList.append(newFreqSet)
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        print('condPattBases :', basePat, condPattBases)
        myCondTree, myHead = createTree(condPattBases, minSup)
        print('head from conditional tree: ', myHead)
        if myHead != None:
            print('conditional tree for: ', newFreqSet)
            myCondTree.disp(1)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList)

if __name__=='__main__':
    simpDat=loadSimpDat()
    initSet=createInitSet(simpDat)
    myFPtree,myHeaderTab=createTree(initSet,3)
    myFreqItems=[]
    mineTree(myFPtree,myHeaderTab,3,set([]),myFreqItems)
    print('myFreqItems=',myFreqItems)

