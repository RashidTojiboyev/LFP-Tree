class TreeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count= numOccur
        self.nodeLink = None # link similar nodes
        self.parent = parentNode
        self.chidren = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind = 1): # DFS to print tree
        print (' ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)

'''
    ======= FP-Tree Construction (like Trie) =======
'''
def createTree(dataSet, minSup = 1): # dataSet is {}
    #   Pass 1: Count frequency
    headerTable = {}
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]

    #   Remove unqualified items
    keysToDel = []
    for k in headerTable.keys():
        if headerTable[k] < minSup:
            keysToDel.append(k)
    for k in keysToDel:
        headerTable.pop(k, None)

    freqItemSet = set(headerTable.keys())
    if len(freqItemSet) == 0: return None, None

    #   Add link field to headerTable and init to None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None] # frequency, link to 1st item

    retTree = TreeNode('Null', 1, None)
    #   Pass 2
    for tranSet, count in dataSet.items():
        localD = {}
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0] # frequent
        if len(localD) > 0:
            # sort by frequent - highest come first
            st = sorted(localD.items(), key=lambda p: p[1], reverse=True)
            orderedItems = [v[0] for v in st]
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable


def updateTree(items, inTree, headerTable, count):
    #   Iterative
    retTree = inTree
    for i in range(len(items)):
        if items[i] in inTree.chidren:
            inTree.chidren[items[i]].inc(count)
        else:
            inTree.chidren[items[i]] = TreeNode(items[i], count, inTree)
            #   Append the Linked List in headerTable
            if headerTable[items[i]][1] == None:
                headerTable[items[i]][1] = inTree.chidren[items[i]]
            else:
                updateHeader(headerTable[items[i]][1], inTree.chidren[items[i]])
        inTree = inTree.chidren[items[i]]
    inTree = retTree # return

def updateHeader(nodeToTest, targetNode): # like a linked-list of similar items
    while(nodeToTest.nodeLink != None): # go to the end of the linked-list
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

'''
    ======= Creating conditional FP trees =======
'''

def ascendTree(leafNode, prefixPath): # bottom up to root
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(treeNode):
    condPats = {}
    while treeNode != None: # do ascending for each instance of the same type
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats

'''
    ======= Mining =======
'''
def mineTree(headerTable, minSup, preFix, freqItemList, level = 0):
    #   start from lowest frequent item
    bigL = [v[0] for v in sorted(headerTable.items(), key = lambda p: p[1][0])]
    #   Based on some existing CP-tree - that is, some stat tree under some condition like p&q
    for basePat in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        freqItemList.append((newFreqSet, headerTable[basePat][0])) # return: freqSet - its occurence

        condPattBases = findPrefixPath(headerTable[basePat][1])
        myCondTree, myHead = createTree(condPattBases, minSup)

        if myHead != None:
            mineTree(myHead, minSup, newFreqSet, freqItemList, level + 1)
